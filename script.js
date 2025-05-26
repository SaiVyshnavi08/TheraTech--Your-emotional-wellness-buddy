document.addEventListener("DOMContentLoaded", function () {
    const emotionResponse = document.getElementById("emotion-response");
    const therapySuggestion = document.getElementById("therapy-suggestion");

    // Automatically fetch emotion every 5 seconds
    setInterval(() => {
        fetch("/analyze_emotion")
            .then(response => response.json())
            .then(data => {
                const emotion = data.emotion;
                emotionResponse.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);

                // Therapy suggestions based on detected emotion
                const suggestions = {
                    happy: "Keep up the great mood! Share a smile or gratitude with someone.",
                    sad: "Take a deep breath. Consider journaling your thoughts or listening to calming music.",
                    angry: "Try a short walk, deep breathing, or some gentle stretches to relax.",
                    anxious: "Breathe deeply. Ground yourself by noticing 5 things you can see around you.",
                    neutral: "Stay centered. Maybe try a mindfulness activity or a positive affirmation.",
                    surprised: "Reflect on what caused the surprise. Was it positive or stressful?",
                    disgusted: "Take a break. Refresh your space or watch something uplifting.",
                    fearful: "You're safe. Try positive visualization or reach out to a friend."
                };

                therapySuggestion.textContent = suggestions[emotion] || "Stay calm and take care of yourself. 💙";
            })
            .catch(error => {
                emotionResponse.textContent = "Error detecting emotion.";
                therapySuggestion.textContent = "Unable to fetch therapy suggestion.";
                console.error("Error:", error);
            });
    }, 5000); // update every 5 seconds
});
