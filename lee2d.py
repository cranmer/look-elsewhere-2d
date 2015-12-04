"""
## Look Elsewhere Effect in 2-d

Kyle Cranmer, Nov 19, 2015

Based on
*Estimating the significance of a signal in a multi-dimensional search* by  
Ofer Vitells and Eilam Gross http://arxiv.org/pdf/1105.4355v1.pdf

This is for the special case of a likelihood function of the form 
$L(\mu, \nu_1, \nu_2)$ where $\mu$ is a single parameter of interest and
$\nu_1,\nu_2$ are two nuisance parameters that are not identified under the null.
For example, $\mu$ is the signal strength of a new particle and $\nu_1,\nu_2$ are the
unknown mass and width of the new particle. Under the null hypothesis, those parameters 
don't mean anything... aka they "are not identified under the null" in the statistics jargon.
This introduces a 2-d look elsewhere effect.

The LEE correction in this case is based on 

\begin{equation}
E[ \phi(A_u) ] = P(\chi^2_1 > u) + e^{-u/2} (N_1 + \sqrt{u} N_2) \,
\end{equation}

where 
   * $A_u$ is the 'excursion set above level $u$ (eg. the set of parameter points 
      in $(\nu_1,\nu_2)$ that have a -2 log-likelihood ratio greater than $u$ )

   * $\phi(A_u)$ is the Euler characteristic of the excursion set

   * $E[ \phi(A_u) ]$ is the expectation of the Euler characteristic of those excursion sets under the null

   * $P(\chi^2_1 > u)$ is the standard chi-square probability 

   * and $N_1$ and $N_2$ are two coefficients that characterize the chi-square random field.

"""

import numpy as np 
import matplotlib.pyplot as plt 
from numpy import exp, sqrt
from scipy.optimize import fsolve
from scipy.stats import chi2
from scipy.ndimage.morphology import *
from scipy.ndimage import *
from scipy.stats import norm

def expected_euler(u, n1, n2):
   """return expected Euler characteristic for given level u and coefficients n1, n2"""
   return chi2.cdf(u, 1) + np.exp(-u/2)*(n1+n2*np.sqrt(u))

def _equations(p,exp_phi_1, exp_phi_2,u1, u2):
   """set of equations to solve to find n1, n2"""
   n1,n2 = p
   return (exp_phi_1-expected_euler(u1,n1,n2), exp_phi_2-expected_euler(u2,n1,n2))

def get_coefficients(u1, u2, exp_phi_1, exp_phi_2):
   """
   Get the coefficients n1 and n2 that correspond to
   having an expected Euler characteristic exp_phi_1 above level u1
   and exp_phi_2 above level u2
   """
   n1, n2 = fsolve(_equations, (1,1), args=(exp_phi_1, exp_phi_2, u1,u2))
   return n1, n2

def global_pvalue(u,n1,n2):
   """
   Return the global p-value for an observed 
   -2log likelihood ratio value u and given n1,n2
   """
   return expected_euler(u,n1,n2)-1.

def do_LEE_correction(max_local_sig, u1, u2, exp_phi_1, exp_phi_2):
   """
   Return the global p-value for an observed local significance 
   after correcting for the look-elsewhere effect
   given expected Euler characteristic exp_phi_1 above level u1
   and exp_phi_2 above level u2
   """
   n1, n2 = get_coefficients(u1,u2,exp_phi_1, exp_phi_2)
   this_global_p = global_pvalue(max_local_sig**2, n1, n2)
   print ' n1, n2 =', n1, n2
   print ' local p_value = %f,  local significance = %f' %(norm.cdf(-max_local_sig), max_local_sig)
   print 'global p_value = %f, global significance = %f' %(this_global_p, -norm.ppf(this_global_p))
   return this_global_p


def calculate_euler_characteristic(a):
   """Calculate the Euler characteristic for level set a"""
   face_filter=np.zeros((2,2))+1
   right_edge_filter = np.array([[1,1]])
   bottom_edge_filter = right_edge_filter.T
   
   n_faces = np.sum(convolve(a,face_filter,mode='constant')>3)
   n_edges = np.sum(convolve(a,right_edge_filter,mode='constant')>1)
   n_edges += np.sum(convolve(a,bottom_edge_filter,mode='constant')>1)
   n_vertices = np.sum(a>0)
   
   EulerCharacteristic = n_vertices-n_edges+n_faces
   print '%d-%d+%d=%d' %(n_vertices,n_edges,n_faces,EulerCharacteristic) 
   
   return n_vertices-n_edges+n_faces   



if __name__ == '__main__':
   #create Fig 3 of http://arxiv.org/pdf/1105.4355v1.pdf
   a = np.zeros((7,7))
   a[1,2]=a[1,3]=a[2,1]=a[2,2]=a[2,3]=a[2,4]=1
   a[3,1]=a[3,2]=a[3,3]=a[3,4]=a[3,5]=1
   a[4,1]=a[4,2]=a[4,3]=a[4,4]=1
   a[5,3]=1
   a[6,0]=a[6,1]=1
   a=a.T
   plt.imshow(a,cmap='gray',interpolation='none')
   if calculate_euler_characteristic(a)==2:
      print "ok, one test passed"
   else:
      print "oops, we have a problem"