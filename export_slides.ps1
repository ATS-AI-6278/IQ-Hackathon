$pptApp = New-Object -ComObject PowerPoint.Application
$pptPath = (Get-Item "Smart_Product_Passport_Project_Presentation.pptx").FullName
Write-Host "Opening: $pptPath"

$presentation = $pptApp.Presentations.Open($pptPath, 0, 0, 0)
$outputFolder = Join-Path (Get-Location).Path "exported_slides"
if (!(Test-Path $outputFolder)) {
    New-Item -ItemType Directory -Path $outputFolder | Out-Null
}

Write-Host "Exporting to $outputFolder..."
# 17 = ppSaveAsPNG
$presentation.SaveAs($outputFolder, 17)
$presentation.Close()
Write-Host "Export complete! Total slides exported:" (Get-ChildItem $outputFolder).Count
