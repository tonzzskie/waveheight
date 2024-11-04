// Toggle the sidebar panel visibility
function togglePanel() {
    const panel = document.getElementById("marineDataPanel");
    if (panel.style.right === "0px") {
        panel.style.right = "-400px";  // Hide the panel
    } else {
        panel.style.right = "0px";  // Show the panel
    }
}
