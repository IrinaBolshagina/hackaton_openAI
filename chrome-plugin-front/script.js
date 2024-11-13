function DOMtoString(selector) {
    if (selector) {
        selector = document.querySelector(selector);
        if (!selector) return "ERROR: querySelector failed to find node"
    } else {
        selector = document.documentElement;
    }
    return selector.outerHTML;
}


document.getElementById('sendButton').addEventListener('click', function() {
    chrome.tabs.query({ active: true, currentWindow: true }).then(function (tabs) {
        var activeTab = tabs[0];
        var activeTabId = activeTab.id;

        return chrome.scripting.executeScript({
            target: { tabId: activeTabId },
            // injectImmediately: true,  // uncomment this to make it execute straight away, other wise it will wait for document_idle
            func: DOMtoString,
            // args: ['body']  // you can use this to target what element to get the html for
        });

    }).then(function (results) {
        parse(results[0].result);
    }).catch(function (error) {
        console.log(error)
    });
});


async function parse(from) {
    let parsedEmail = "";
    let parsedFullDescription = "";
    let parsedExpertises = "";

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = from;

    // Get all flex items
    const flexItems = tempDiv.querySelectorAll('.flex-item');
    flexItems.forEach(item => {
        const label = item.querySelector('.show-left');
        const value = item.querySelector('.show-right');

        if (label && value) {
            if (label.innerText.includes("Email")) {
                parsedEmail = value.innerText.trim();
            } else if (label.innerText.includes("Full description")) {
                parsedFullDescription = value.getAttribute('data-markdownable');
            } else if (label.innerText.includes("Expertises")) {
                parsedExpertises = value.innerText.trim();
            }
        }
    });

    await sendFile();
    let resp = await sendJSON(parsedEmail, parsedFullDescription, parsedExpertises);
    console.log(resp)
    // Log the results to the console (or handle them as needed)
    // console.log("Email:", parsedEmail);
    // console.log("Full Description:", parsedFullDescription);
    // console.log("Expertises:", parsedExpertises);
}

async function sendJSON(email, fullDescription, expertises) {
    const req = {
        "email": email,
        "description": fullDescription,
        "expertises": expertises
    }

    const resp = await fetch("http://127.0.0.1:5000/submit_json", {
        method: "POST",
        headers: {
            'Content-type': 'application/json'
        },
        body: JSON.stringify(req)
    });


    return await resp.json();
}

async function sendFile() {
    const fileInput = document.getElementById("cvFile");
    const file = fileInput.files[0]; // Get the selected file

    if (!file) {
        alert("Please select a file first!");
        return;
    }

    // Create a FormData object
    const formData = new FormData();
    formData.append("file", file);

    const resp = await fetch("http://127.0.0.1:5000/submit_pdf", {
        method: 'POST',
        body: formData,
    });

    return await resp.json()
}
