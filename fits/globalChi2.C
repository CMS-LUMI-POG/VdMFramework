#include "Fit/Fitter.h"
#include "Fit/BinData.h"
#include "Fit/Chi2FCN.h"
#include "TH1.h"
#include "TList.h"
#include "Math/WrappedMultiTF1.h"
#include "Math/FitMethodFunction.h"
#include "HFitInterface.h"
#include "TCanvas.h"
#include "TStyle.h"


// definition of shared parameter
// Luminometer1 (PCC) function 
int iparPCC[6] = { 0, // Sigma
                 1, // sigma_{1}/sigma_{2}
		 2, // Amp
		 3, // Frac
		 4, // Mean
		 5  // Const
};

//  Luminometer2 (TrkVtx) function 
int iparTrkVtx[5] = { 0, // Sigma (common parameter)
                  1, // sigma_{1}/sigma_{2} (common parameter)
                  6, // Amp
                  3, // Frac (common parameter)
                  7  // Mean
};

class GlobalChi2 : public ROOT::Math::FitMethodFunction { 

public:
   GlobalChi2( int dim, int npoints, ROOT::Math::FitMethodFunction & f1,  ROOT::Math::FitMethodFunction & f2) :
      ROOT::Math::FitMethodFunction(dim,npoints),
      fChi2_1(&f1), fChi2_2(&f2) {}


   ROOT::Math::IMultiGenFunction * Clone() const { 
      // copy using default copy-ctor
      // i.e. function pointer will be copied (and not the functions)
      return new GlobalChi2(*this);   
   }

   double  DataElement(const double *par, unsigned int ipoint, double *g = 0) const { 
      // implement evaluation of single chi2 element
      double p1[2];
      for (int i = 0; i < 2; ++i) p1[i] = par[iparPCC[i] ];

      double p2[5]; 
      for (int i = 0; i < 5; ++i) p2[i] = par[iparTrkVtx[i] ];

      double g1[2]; 
      double g2[5];
      double value = 0; 
      if (g != 0) { 
         for (int i = 0; i < 6; ++i) g[i] = 0; 
      }

      if (ipoint < fChi2_1->NPoints() ) {
         if (g != 0) { 
            value = fChi2_1->DataElement(p1, ipoint, g1);
            // update gradient values
            for (int i= 0; i < 2; ++i) g[iparPCC[i]] = g1[i];         
         }
         else 
            // no need to compute gradient in this case
            value = fChi2_1->DataElement(p1, ipoint);
      }
      else { 
         unsigned int jpoint = ipoint- fChi2_1->NPoints();
         assert (jpoint < fChi2_2->NPoints() );
         if ( g != 0) { 
            value =  fChi2_2->DataElement(p2, jpoint, g2);
            // update gradient values
            for (int i= 0; i < 5; ++i) g[iparTrkVtx[i]] = g2[i];
         }
         else 
            // no need to compute gradient in this case
            value =  fChi2_2->DataElement(p2, jpoint);
      }
        
      return value; 
      
   }


   // needed if want to use Fumili or Fumili2
   virtual Type_t Type() const { return ROOT::Math::FitMethodFunction::kLeastSquare; }

private:

   virtual double DoEval (const double *par) const {
      double p1[5];
      for (int i = 0; i < 6; ++i) p1[i] = par[iparPCC[i] ];

      double p2[5]; 
      for (int i = 0; i < 5; ++i) p2[i] = par[iparTrkVtx[i] ];

      return (*fChi2_1)(p1) + (*fChi2_2)(p2);
   } 

   const  ROOT::Math::FitMethodFunction * fChi2_1;
   const  ROOT::Math::FitMethodFunction * fChi2_2;
};
