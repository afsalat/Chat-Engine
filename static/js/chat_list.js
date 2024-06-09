
function handleDivClick(id) {

    var divText = document.getElementById(id).innerText;
    u_name = divText
    var outputDiv = document.getElementById('contact_name');

    if (outputDiv === divText){
        console.log("currest!!");
    }
    else{
        outputDiv.textContent = divText;
    }

}
