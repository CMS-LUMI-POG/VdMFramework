{
//=========Macro generated from canvas: c1/c1
//=========  (Sun Feb  7 16:33:52 2016) by ROOT version5.34/32
   TCanvas *c1 = new TCanvas("c1", "c1",0,0,700,500);
   gStyle->SetOptFit(1);
   gStyle->SetOptStat(0);
   c1->SetHighLightColor(2);
   c1->Range(-4.470349e-08,8748231,6,9187259);
   c1->SetFillColor(0);
   c1->SetBorderMode(0);
   c1->SetBorderSize(2);
   c1->SetFrameBorderMode(0);
   c1->SetFrameBorderMode(0);
   
   TGraphErrors *gre = new TGraphErrors(25);
   gre->SetName("");
   gre->SetTitle("4266 PCC DGConst xsec");
   gre->SetFillColor(1);
   gre->SetMarkerStyle(8);
   gre->SetMarkerSize(0.4);
   gre->SetPoint(0,1,9029855);
   gre->SetPointError(0,0,0);
   gre->SetPoint(1,1,9004511);
   gre->SetPointError(1,0,0);
   gre->SetPoint(2,1,9034537);
   gre->SetPointError(2,0,0);
   gre->SetPoint(3,1,9043932);
   gre->SetPointError(3,0,0);
   gre->SetPoint(4,1,9040322);
   gre->SetPointError(4,0,0);
   gre->SetPoint(5,2,9059727);
   gre->SetPointError(5,0,0);
   gre->SetPoint(6,2,9045561);
   gre->SetPointError(6,0,0);
   gre->SetPoint(7,2,9054790);
   gre->SetPointError(7,0,0);
   gre->SetPoint(8,2,9000120);
   gre->SetPointError(8,0,0);
   gre->SetPoint(9,2,9045061);
   gre->SetPointError(9,0,0);
   gre->SetPoint(10,3,8828929);
   gre->SetPointError(10,0,0);
   gre->SetPoint(11,3,8935176);
   gre->SetPointError(11,0,0);
   gre->SetPoint(12,3,8824094);
   gre->SetPointError(12,0,0);
   gre->SetPoint(13,3,8951760);
   gre->SetPointError(13,0,0);
   gre->SetPoint(14,3,8821402);
   gre->SetPointError(14,0,0);
   gre->SetPoint(15,4,9065842);
   gre->SetPointError(15,0,0);
   gre->SetPoint(16,4,9018499);
   gre->SetPointError(16,0,0);
   gre->SetPoint(17,4,8976148);
   gre->SetPointError(17,0,0);
   gre->SetPoint(18,4,9035284);
   gre->SetPointError(18,0,0);
   gre->SetPoint(19,4,9014709);
   gre->SetPointError(19,0,0);
   gre->SetPoint(20,5,9044957);
   gre->SetPointError(20,0,0);
   gre->SetPoint(21,5,9001571);
   gre->SetPointError(21,0,0);
   gre->SetPoint(22,5,9103837);
   gre->SetPointError(22,0,0);
   gre->SetPoint(23,5,9045304);
   gre->SetPointError(23,0,0);
   gre->SetPoint(24,5,9114087);
   gre->SetPointError(24,0,0);
   
   TH1F *Graph_Graph1 = new TH1F("Graph_Graph1","4266 PCC DGConst xsec",100,0.6,5.4);
   Graph_Graph1->SetMinimum(8792134);
   Graph_Graph1->SetMaximum(9143356);
   Graph_Graph1->SetDirectory(0);
   Graph_Graph1->SetStats(0);

   Int_t ci;      // for color index setting
   TColor *color; // for color definition with alpha
   ci = TColor::GetColor("#000099");
   Graph_Graph1->SetLineColor(ci);
   Graph_Graph1->GetXaxis()->SetTitle("Scanpair");
   Graph_Graph1->GetXaxis()->SetLabelFont(42);
   Graph_Graph1->GetXaxis()->SetLabelSize(0.035);
   Graph_Graph1->GetXaxis()->SetTitleSize(0.035);
   Graph_Graph1->GetXaxis()->SetTitleFont(42);
   Graph_Graph1->GetYaxis()->SetTitle("xsec");
   Graph_Graph1->GetYaxis()->SetLabelFont(42);
   Graph_Graph1->GetYaxis()->SetLabelSize(0.035);
   Graph_Graph1->GetYaxis()->SetTitleSize(0.035);
   Graph_Graph1->GetYaxis()->SetTitleFont(42);
   Graph_Graph1->GetZaxis()->SetLabelFont(42);
   Graph_Graph1->GetZaxis()->SetLabelSize(0.035);
   Graph_Graph1->GetZaxis()->SetTitleSize(0.035);
   Graph_Graph1->GetZaxis()->SetTitleFont(42);
   gre->SetHistogram(Graph_Graph1);
   
   gre->Draw("ap");
   
   TPaveText *pt = new TPaveText(0.2881322,0.94,0.7118678,0.995,"blNDC");
   pt->SetName("title");
   pt->SetBorderSize(0);
   pt->SetFillColor(0);
   pt->SetFillStyle(0);
   pt->SetTextFont(42);
   TText *text = pt->AddText("4266 PCC DGConst xsec");
   pt->Draw();
   c1->Modified();
   c1->cd();
   c1->SetSelected(c1);
}
