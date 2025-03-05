import numpy as np


def x_to_t(x):
    """Convert from cartesian to spherical coordinates. Works in n dimension.
    
    Parameters
    ----------
    x : np.ndarray
        Cartesian coordinates (x1,x2,x3, ... , xn)
        
    Returns
    -------
    np.ndarray
        Spherical coordinates (r, theta_1, theta_2, ... , theta_n-1)
    """
    ndim = len(x)
    res = np.full((ndim), np.nan)
    r = np.linalg.norm( x )
    res[0] = r
    for i in range(1, ndim-1):
        res[i] =  np.arctan2(  np.linalg.norm( x[i:] ) , x[i-1] )
        
    res[ndim-1] =  np.arctan2( x[ndim-1]  , x[ndim-2] )
    return res


def t_to_x( t ):
    """Convert from spherical to cartesian coordinates. Works in n dimension.
    
    Parameters
    ----------
    t : np.ndarray
        Spherical coordinates (r, theta_1, theta_2, ... , theta_n-1)

    Returns
    -------
    np.ndarray
        Cartesian coordinates (x1,x2,x3, ... , xn)
    """
    ndim = len(t)
    res = np.full((ndim), np.nan, dtype = float)
    for i in range(0,ndim-1) :
        res[i] =  np.prod( np.sin( t[1:i+1] ) ) * np.cos( t[i+1] )
        
    res[ndim-1] =  np.prod( np.sin( t[1:ndim-1] ) ) * np.sin( t[ndim-1] )
    return res * t[0]


if __name__ == "__main__":
    x = [ 0.2 ,0.6 , 0.4 , 0.6]
    t =  x_to_t( x )
    x_back =  t_to_x( t )
    print (x)
    print (x_back)
    assert(np.isclose(x, x_back).all())

    
    
    

    