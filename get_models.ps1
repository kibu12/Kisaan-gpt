$envParams = Get-Content -Path E:\projects\kisaan_gpt_project\kisaan_gpt\.env | Where-Object { $_ -match '=' } | ForEach-Object {
    $parts = $_ -split '=', 2
    @{ $parts[0].Trim() = $parts[1].Trim() }
}
$key = ""
foreach ($item in $envParams) {
    if ($item.Keys -contains "GROQ_API_KEY") {
        $key = $item["GROQ_API_KEY"]
    }
}
$key = $key -replace '"', ''
curl.exe -H "Authorization: Bearer $key" https://api.groq.com/openai/v1/models > E:\projects\kisaan_gpt_project\kisaan_gpt\models_curl.txt
