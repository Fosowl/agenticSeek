import axios from 'axios';

const API_KEY = "AIzaSyCH78cTqVOKG1Z1go75SPGISfFU_ibDXNc";

async function listModels() {
    console.log(`Listing available models...`);

    const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${API_KEY}`;

    try {
        console.log(`Sending request to: ${url}`);
        const response = await axios.get(url);

        console.log("Response Status:", response.status);
        console.log("Available Models:");

        const data = response.data as any;
        if (data && data.models) {
             data.models.forEach((m: any) => {
                 console.log(`- ${m.name} (${m.supportedGenerationMethods})`);
             });
        } else {
            console.log("No models found in response.");
        }

    } catch (error: any) {
        if (error.response) {
             console.error("Axios Error:");
            console.error("Status:", error.response?.status);
            console.error("Data:", error.response?.data);
        } else {
            console.error("Error:", error);
        }
    }
}

listModels();
