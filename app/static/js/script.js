function showHideElement(elementId) {
  let eleId = document.getElementById(elementId);
  if (eleId.style.display === "none") {
    eleId.style.display = "block"; 
  } else {
    eleId.style.display = "none";
  }
}