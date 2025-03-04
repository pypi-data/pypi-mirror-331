#return the 31 DPM model parameters, for our favored models.  

def returnmodelparams(modelID):

    if(modelID.startswith("ClusterBased5") | modelID.startswith("Model1")):
        Pnorm12 = 4.093e+02
        alphatrP12 = 1.3
        alphahiP12 = 4.1
        alphaloP12 = 0.3
        c500P = 1.8
        alphatrPMvar = 0.0
        alphahiPMvar = 0.0 
        alphaloPMvar = 0.0
        betaP = 2/3.
        gammaP = 8/3.
        nenorm12 = 5.86e-04
        alphatrne12 = 1.9
        alphahine12 = 2.7
        alphalone12 = 1.0
        c500ne = 1.8
        alphatrneMvar = 0.0
        alphahineMvar = 0.0
        alphaloneMvar = 0.0
        betane = 0.0
        gammane = 2. 
        sigmalogne = 0.01
        Znorm12 = 0.3
        alphatrZ12 = 0.5
        alphahiZ12 = 0.7
        alphaloZ12 = 0.0
        c500Z = 1.8
        alphatrZMvar = 0.0
        alphahiZMvar = 0.0
        alphaloZMvar = 0.0
        betaZ = 0.0
        gammaZ = 0.0
        
    if(modelID.startswith("ClusterScaled5") | modelID.startswith("Model2")):
        Pnorm12 = 1.1535e+02
        alphatrP12 = 1.3
        alphahiP12 = 4.1
        alphaloP12 = 0.3
        c500P = 1.8
        alphatrPMvar = 0.0
        alphahiPMvar = 0.0 
        alphaloPMvar = 0.0
        betaP = 0.85
        gammaP = 8/3.
        nenorm12 = 4.874e-05
        alphatrne12 = 1.9
        alphahine12 = 2.7
        alphalone12 = 1.0
        c500ne = 1.8
        alphatrneMvar = 0.0
        alphahineMvar = 0.0
        alphaloneMvar = 0.0
        betane = 0.36
        gammane = 2. 
        sigmalogne = 0.01
        Znorm12 = 0.3
        alphatrZ12 = 0.5
        alphahiZ12 = 0.7
        alphaloZ12 = 0.0
        c500Z = 1.8
        alphatrZMvar = 0.0
        alphahiZMvar = 0.0
        alphaloZMvar = 0.0
        betaZ = 0.0
        gammaZ = 0.0
 
    if(modelID.startswith("ClusterGroupScaled5") | modelID.startswith("Model3")):
        Pnorm12 = 7.07e+01
        alphatrP12 = 0.2
        alphahiP12 = 2.0
        alphaloP12 = -0.6
        c500P = 1.8
        alphatrPMvar = 0.3667
        alphahiPMvar = 0.7
        alphaloPMvar = 0.3
        betaP = 0.92
        gammaP = 8/3. 
        nenorm12 = 4.874e-05
        alphatrne12 = 0.45
        alphahine12 = 0.50
        alphalone12 = 0.40
        c500ne = 1.8
        alphatrneMvar = 0.483
        alphahineMvar = 0.733
        alphaloneMvar = 0.2
        betane = 0.36
        gammane = 2. 
        sigmalogne = 0.01
        Znorm12 = 0.3
        alphatrZ12 = 0.5
        alphahiZ12 = 0.7
        alphaloZ12 = 0.0
        c500Z = 1.8
        alphatrZMvar = 0.0
        alphahiZMvar = 0.0
        alphaloZMvar = 0.0
        betaZ = 0.0
        gammaZ = 0.0

    if(modelID.endswith("disp")):
        sigmalogne = 0.30
    if(modelID.endswith("ldisp")):
        sigmalogne = 0.15

    return(Pnorm12,alphatrP12,alphahiP12,alphaloP12,c500P,alphatrPMvar,alphahiPMvar,alphaloPMvar,betaP,gammaP,nenorm12,alphatrne12,alphahine12,alphalone12,c500ne,alphatrneMvar,alphahineMvar,alphaloneMvar,betane,gammane,sigmalogne,Znorm12,alphatrZ12,alphahiZ12,alphaloZ12,c500Z,alphatrZMvar,alphahiZMvar,alphaloZMvar,betaZ,gammaZ)
