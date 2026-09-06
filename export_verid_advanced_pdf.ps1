$pptPath = 'C:\Users\acer\Pictures\IQ\output\pptx\Verid_Household_Intelligence_OS_Advanced.pptx'
$pdfDir = 'C:\Users\acer\Pictures\IQ\output\pdf'
$pdfPath = Join-Path $pdfDir 'Verid_Household_Intelligence_OS_Advanced.pdf'
New-Item -ItemType Directory -Force -Path $pdfDir | Out-Null
$app = New-Object -ComObject PowerPoint.Application
try {
    $presentation = $app.Presentations.Open($pptPath, 0, 0, 0)
    $presentation.SaveAs($pdfPath, 32)
    $presentation.Close()
}
finally {
    $app.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($app)
}
Write-Output $pdfPath
