import ROOT
import os


from Analysis.Tools.helpers import getObjFromFile



maps_ele =           {"medium": "egammaEffi_EGM2D_Medium.root",
                      "tight":  "egammaEffi_EGM2D_Tight.root",
                      "loose":  "egammaEffi_EGM2D_Loose.root",
                      "Vloose": "egammaEffi_EGM2D_VLoose.root",
                     }

maps_mu =            {"tight":  [("NUM_LeptonMvaTight_DEN_TrackerMuons_abseta_pt.root","NUM_LeptonMvaTight_DEN_TrackerMuons_abseta_pt")],
                      "medium": [("NUM_LeptonMvaMedium_DEN_TrackerMuons_abseta_pt.root","NUM_LeptonMvaMedium_DEN_TrackerMuons_abseta_pt")],
                      "loose":  [("NUM_LeptonMvaLoose_DEN_TrackerMuons_abseta_pt.root","NUM_LeptonMvaLoose_DEN_TrackerMuons_abseta_pt")],
                      "Vloose": [("NUM_LeptonMvaVLoose_DEN_TrackerMuons_abseta_pt.root","NUM_LeptonMvaVLoose_DEN_TrackerMuons_abseta_pt")],
                     }

class LeptonSF:
    def __init__(self, era, ID = None):

        if era not in ["UL2016_preVFP", "UL2016", "UL2017", "UL2018" ]:
            raise Exception("Lepton SF for era %i not known"%era)

        self.dataDir = "$CMSSW_BASE/src/Analysis/Tools/data/leptonSFData/LeptonMva_v1"
        self.era = era

        self.SFmaps = {
            "elec" : {
                "SF" :  getObjFromFile(self.dataDir+"/"+self.era+"/"+maps_el[ID],"EGamma_SF2D"),
                "syst": getObjFromFile(self.dataDir+"/"+self.era+"/"+maps_el[ID],"sys"),
                "stat": getObjFromFile(self.dataDir+"/"+self.era+"/"+maps_el[ID],"stat"),
            },
            "muon" : {
                "SF" :  [getObjFromFile(os.path.expandvars(os.path.join(self.dataDir+"/"+self.era, file)), key) for (file, key) in maps_mu[ID]],
                "syst": [getObjFromFile(os.path.expandvars(os.path.join(self.dataDir+"/"+self.era, file)), key+"_syst") for (file, key) in maps_mu[ID]],
                "stat": [getObjFromFile(os.path.expandvars(os.path.join(self.dataDir+"/"+self.era, file)), key+"_stat") for (file, key) in maps_mu[ID]],
            }
        }


    def getSF(self, pdgId, pt, eta, unc='syst', sigma=0):
        uncert = "syst"
        if unc == "stat":
            uncert = "stat"
        lepton = None
        if abs(pdgId)==11:
            lepton = "elec"
            if eta > 2.5:
                eta = 2.49
            if eta < -2.5:
                eta = -2.49
            if pt > 200:
                pt = 199

            etabin = self.SFmaps[lepton]["SF"].GetXaxis().FindBin(eta)
            ptbin  = self.SFmaps[lepton]["SF"].GetYaxis().FindBin(pt)
            SF = self.SFmaps[lepton]["SF"].GetBinContent(etabin, ptbin)
            err = self.SFmaps[lepton][uncert].GetBinContent(etabin, ptbin)


        elif abs(pdgId)==13:
            lepton = "muon"
            eta = abs(eta)
            if eta > 2.4:
                eta = 2.39
            if pt > 120:
                pt = 119
            etabin = self.SFmaps[lepton]["SF"][0].GetXaxis().FindBin(eta)
            ptbin  = self.SFmaps[lepton]["SF"][0].GetYaxis().FindBin(pt)
            SF = self.SFmaps[lepton]["SF"][0].GetBinContent(etabin, ptbin)
            err = self.SFmaps[lepton][uncert][0].GetBinContent(etabin, ptbin)

        else:
          raise Exception("Lepton SF for PdgId %i not known"%pdgId)

        return SF+sigma*err