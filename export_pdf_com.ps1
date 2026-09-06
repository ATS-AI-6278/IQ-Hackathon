$pptApp = New-Object -ComObject PowerPoint.Application
$pptPath = "C:\Users\acer\Pictures\IQ\Smart_Product_Passport_Project_Presentation.pptx"
$pres = $pptApp.Presentations.Open($pptPath, 0, 0, 0)
$outPdf = "C:\Users\acer\Desktop\antigravity_created\Verid_Household_OS_Native_Vector.pdf"
# 32 = ppSaveAsPDF
$pres.SaveAs($outPdf, 32)
$pres.Close()
Write-Host "PowerPoint native PDF export success: $outPdf"
