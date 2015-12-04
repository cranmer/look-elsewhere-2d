import numpy as np 
from numpy import exp, sqrt
import ROOT

def create_test_scan(nx=50,ny=100, n_components=10):
   xarray = np.arange(-1,1,1./nx)
   yarray = np.arange(-1,1,1./ny)
   xx,yy = np.meshgrid(xarray,yarray)
   xmeans = 2*np.random.rand(n_components)-1.
   ymeans = 2*np.random.rand(n_components)-1.
   amps = np.random.chisquare(1,n_components)
   zz = xx*0
   for i, amp in enumerate(amps):
      xmean, ymean = xmeans[i], ymeans[i]
      zz += amp*np.exp(-((xx-xmean)**2+(yy-ymean)**2)/(2.*0.3**4))
   return xx, yy, zz

def create_test_histograms(nHists=25, nx=50,ny=100, n_components=10, fname='test_hists.root'):
   f_ = ROOT.TFile(fname,'RECREATE')
   for i in range(nHists):
      xx, yy, zz = create_test_scan(nx, ny, n_components)
      hist = ROOT.TH2F('scan_toy_%d' %(i), 'test', nx, np.min(xx), np.max(xx), ny, np.min(yy), np.max(yy))
      for x, y, z in zip(np.hstack(xx),np.hstack(yy),np.hstack(zz)):
         hist.Fill(x, y, z)
      hist.Write()
   f_.Write()
   f_.Close()

def convert_hist_to_numpy(hist):
   ''' a little helper script'''
   temp = np.zeros((hist.GetNbinsX(), hist.GetNbinsY()))
   for i in range(temp.shape[0]):
      for j in range(temp.shape[1]):
         temp[i,j] = hist.GetBinContent(i+1, j+1)
   return temp
