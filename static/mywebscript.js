let RunSentimentAnalysis = ()=>{
    let textToAnalyze = document.getElementById("textToAnalyze").value;
    let systemResponse = document.getElementById("system_response");

    let xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.responseText) {
                systemResponse.innerHTML = this.responseText;
            } else {
                systemResponse.innerHTML = "The emotion detection service could not be reached. Please try again later.";
            }
        }
    };
    xhttp.open("POST", "emotionDetector", true);
    xhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8");
    xhttp.send("textToAnalyze=" + encodeURIComponent(textToAnalyze));
}
