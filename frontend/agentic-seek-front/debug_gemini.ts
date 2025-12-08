import axios from 'axios';

// This script expects the API key to be passed as an environment variable or argument.
// Example: GEMINI_API_KEY=your_key npx ts-node debug_gemini.ts

const API_KEY = process.env.GEMINI_API_KEY;

if (!API_KEY) {
    console.error("Error: GEMINI_API_KEY environment variable is not set.");
    process.exit(1);
}

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
