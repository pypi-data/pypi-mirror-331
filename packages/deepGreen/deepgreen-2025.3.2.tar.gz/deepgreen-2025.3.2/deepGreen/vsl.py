import torch
import numpy as np

'''
VS-Lite in PyTorch
@author: Feng Zhu (fengzhu@ucar.edu)
'''

class VSL(torch.nn.Module):
    def __init__(self, T1=8, T2=23, M1=0.01, M2=0.05, Mmax=0.76, Mmin=0.01, 
                 alph=0.093, m_th=4.886, mu_th=5.8, rootd=1000, I_0=1, I_f=12):
        """
        Initialize the VS-Lite model with parameters.
        
        Parameters:
        - T1, T2: Temperature thresholds for growth response.
        - M1, M2: Soil moisture thresholds for growth response.
        - Mmax, Mmin: Maximum and minimum soil moisture.
        - alph, m_th, mu_th: Parameters for the Leaky Bucket model.
        - rootd: Root depth (mm).
        - I_0, I_f: Integration window start and end months.
        """
        super().__init__()
        self.T1 = torch.nn.Parameter(torch.tensor(T1, dtype=torch.float32))
        self.T2 = torch.nn.Parameter(torch.tensor(T2, dtype=torch.float32))
        self.M1 = torch.nn.Parameter(torch.tensor(M1, dtype=torch.float32))
        self.M2 = torch.nn.Parameter(torch.tensor(M2, dtype=torch.float32))
        self.Mmax = torch.tensor(Mmax)
        self.Mmin = torch.tensor(Mmin)
        self.alph = torch.tensor(alph)
        self.m_th = torch.tensor(m_th)
        self.mu_th = torch.tensor(mu_th)
        self.rootd = torch.tensor(rootd)
        self.I_0 = torch.tensor(I_0)
        self.I_f = torch.tensor(I_f)

    def compute_gT(self, T):
        """
        Compute the temperature-based growth response.
        """
        gT = (T - self.T1) / (self.T2 - self.T1)
        gT = torch.clamp(gT, 0, 1)  # Clamp between 0 and 1
        return gT

    def compute_gM(self, M):
        """
        Compute the moisture-based growth response.
        """
        gM = (M - self.M1) / (self.M2 - self.M1)
        gM = torch.clamp(gM, 0, 1)  # Clamp between 0 and 1
        return gM

    def compute_gE(self, phi):
        """
        Compute the insolation-based growth response.
        """
        latr = phi * torch.pi / 180  # Convert latitude to radians
        ndays = torch.tensor([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])  # Days in each month
        cdays = torch.cumsum(ndays, dim=0)  # Cumulative days
        jday = torch.arange(1, 366)  # Days of the year

        # Solar declination
        sd = torch.asin(torch.sin(torch.tensor(torch.pi * 23.5 / 180)) * torch.sin(torch.tensor(torch.pi * (jday - 80) / 180)))

        # Compute normalized daylength
        y = -torch.tan(latr) * torch.tan(sd)
        y = torch.clamp(y, -1, 1)
        hdl = torch.acos(y)
        dtsi = (hdl * torch.sin(latr) * torch.sin(sd)) + (torch.cos(latr) * torch.cos(sd) * torch.sin(hdl))
        ndl = dtsi / torch.max(dtsi)  # Normalized day length

        # Compute mean monthly insolation (m_star)
        jday_mid = cdays[:-1] + 0.5 * ndays[1:]  # Middle of each month
        m_star = 1 - torch.tan(latr) * torch.tan(23.439 * torch.pi / 180 * torch.cos(jday_mid * torch.pi / 182.625))
        m_star = torch.clamp(m_star, 0, 2)  # Apply constraints

        # Compute monthly mean daylength
        gE = torch.zeros(12)
        for t in range(12):
            gE[t] = torch.mean(ndl[cdays[t]:cdays[t+1]])

        return gE

    def leakybucket_monthly(self, syear, eyear, phi, T, P, Mmax=0.76, Mmin=0.01, alph=0.093, m_th=4.886, mu_th=5.8, rootd=1000, M0=0.2):
        """
        Simulate soil moisture using the CPC Leaky Bucket model in PyTorch.
        """
        iyear = torch.arange(syear, eyear + 1)
        nyrs = len(iyear)

        if T.dim() == 1:
            T = T.view(nyrs, 12).T
        if P.dim() == 1:
            P = P.view(nyrs, 12).T

        # Output tensors
        M = torch.empty((12, nyrs))
        potEv = torch.empty((12, nyrs))

        # Compute normalized daylength
        latr = phi * torch.pi / 180  # Convert latitude to radians
        ndays = torch.tensor([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
        cdays = torch.cumsum(ndays, dim=0)
        jday = torch.arange(1, 366)
        sd = torch.asin(torch.sin(torch.tensor(torch.pi * 23.5 / 180)) * torch.sin(torch.tensor(torch.pi * (jday - 80) / 180)))
        y = -torch.tan(latr) * torch.tan(sd)
        y = torch.clamp(y, -1, 1)
        hdl = torch.acos(y)
        dtsi = (hdl * torch.sin(latr) * torch.sin(sd)) + (torch.cos(latr) * torch.cos(sd) * torch.sin(hdl))
        ndl = dtsi / torch.max(dtsi)

        # Mean monthly daylength
        jday_mid = cdays[:-1] + 0.5 * ndays[1:]
        m_star = 1 - torch.tan(latr) * torch.tan(23.439 * torch.pi / 180 * torch.cos(jday_mid * torch.pi / 182.625))
        m_star = torch.clamp(m_star, 0, 2)
        nhrs = 24 * torch.acos(1 - m_star) / torch.pi
        L = (ndays[1:] / 30) * (nhrs / 12)

        for cyear in range(nyrs):
            for t in range(12):
                # Compute potential evapotranspiration
                if T[t, cyear] < 0:
                    Ep = 0
                elif T[t, cyear] < 26.5:
                    istar = torch.clamp(T[:, cyear] / 5, min=0)
                    I = torch.sum(istar ** 1.514)
                    a = (6.75e-7) * I ** 3 - (7.71e-5) * I ** 2 + (1.79e-2) * I + 0.49
                    Ep = 16 * L[t] * (10 * T[t, cyear] / I) ** a
                else:
                    Ep = -415.85 + 32.25 * T[t, cyear] - 0.43 * T[t, cyear] ** 2

                potEv[t, cyear] = Ep

                # Compute soil moisture
                if t > 0:
                    prev_M = M[t - 1, cyear]
                elif cyear > 0:
                    prev_M = M[11, cyear - 1]
                else:
                    prev_M = M0

                Etrans = Ep * prev_M * rootd / (Mmax * rootd)
                G = mu_th * alph / (1 + mu_th) * prev_M * rootd
                R = P[t, cyear] * (prev_M * rootd / (Mmax * rootd)) ** m_th + (alph / (1 + mu_th)) * prev_M * rootd
                dWdt = P[t, cyear] - Etrans - R - G

                M[t, cyear] = prev_M + dWdt / rootd
                M[t, cyear] = torch.clamp(M[t, cyear], Mmin, Mmax)

        return {
            'M': M,
            'potEv': potEv,
            'ndl': ndl,
            'cdays': cdays
        }


    def forward(self, syear, eyear, phi, T, P):
        """
        Forward pass of the VS-Lite model.
        
        Parameters:
        - syear, eyear: Start and end years of the simulation.
        - phi: Latitude of the site (degrees).
        - T: Monthly temperature (12 x Nyrs).
        - P: Monthly precipitation (12 x Nyrs).
        """
        iyear = torch.arange(syear, eyear + 1)
        nyrs = len(iyear)
        T = torch.tensor(T.reshape((nyrs, 12)).T)
        P = torch.tensor(P.reshape((nyrs, 12)).T)
        phi = torch.tensor(phi)

        # Compute soil moisture
        lb_res = self.leakybucket_monthly(syear, eyear, phi, T, P)
        M, potEv = lb_res['M'], lb_res['potEv']

        # Compute growth responses
        gT = self.compute_gT(T)
        gM = self.compute_gM(M)
        gE = self.compute_gE(phi)

        # Compute overall growth response
        Gr = torch.min(gT, gM) * gE.unsqueeze(1)

        # Integrate growth response over the integration window
        width = torch.zeros(nyrs)
        width[:] = torch.nan
        if phi > 0:  # Northern Hemisphere
            if self.I_0 < 0:
                startmo = 12 + self.I_0
                endmo = self.I_f
                width[0] = torch.sum(Gr[0:endmo, 0]) + torch.sum(torch.mean(Gr[startmo-1:12, :], dim=1))
                for cyear in range(1, nyrs):
                    width[cyear] = torch.sum(Gr[startmo-1:12, cyear-1]) + torch.sum(Gr[0:endmo, cyear])
            else:
                startmo = self.I_0
                endmo = self.I_f
                for cyear in range(nyrs):
                    width[cyear] = torch.sum(Gr[startmo-1:endmo, cyear])
        else:  # Southern Hemisphere
            startmo = 6 + self.I_0
            endmo = self.I_f - 6
            width = torch.zeros(nyrs)
            for cyear in range(nyrs-1):
                width[cyear] = torch.sum(Gr[startmo-1:12, cyear]) + torch.sum(Gr[0:endmo, cyear+1])
            width[nyrs-1] = torch.sum(Gr[startmo-1:12, nyrs-1]) + torch.sum(torch.mean(Gr[0:endmo, :], dim=1))

        # Standardize the ring width index
        trw = (width - torch.mean(width)) / torch.std(width)

        res = {
            'trw': trw,
            'gT': gT,
            'gM': gM,
            'gE': gE,
            'Gr': Gr,
            'M': M,
            'potEv': potEv,
            'width': width,
            'width_mean': torch.mean(width),
            'width_std': torch.std(width),
        }

        return res

    def training_step(self, batch, batch_idx):
        x, y = batch
        predictions = self(x)
        loss = self.criterion(predictions, y)
        self.log('train_loss', loss, on_step=True, on_epoch=True, prog_bar=True, sync_dist=True)
        self.log('T1', self.T1, on_step=True, on_epoch=True, prog_bar=True, sync_dist=True)
        self.log('T2', self.T2, on_step=True, on_epoch=True, prog_bar=True, sync_dist=True)
        self.log('M1', self.M1, on_step=True, on_epoch=True, prog_bar=True, sync_dist=True)
        self.log('M2', self.M2, on_step=True, on_epoch=True, prog_bar=True, sync_dist=True)

        # Log gradients
        for name, param in self.named_parameters():
            if param.grad is not None:
                self.log(f"{name}_grad", param.grad.abs().mean())

        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        predictions = self(x)
        loss = self.criterion(predictions, y)
        self.log('valid_loss', loss, on_step=True, on_epoch=True, prog_bar=True, sync_dist=True)
        return loss

    def test_step(self, batch, batch_idx):
        x, y = batch
        predictions = self(x)
        loss = self.criterion(predictions, y)
        self.log('test_loss', loss, sync_dist=True)
        return loss
    
    def configure_optimizers(self):
        return torch.optim.Adam([{'params': [self.T1, self.T2, self.M1, self.M2], 'lr': self.lr}])