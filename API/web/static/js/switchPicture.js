function switchPhoto() {
  // Get the checkbox
  var buttonPicture = document.getElementById("buttonPicture");
  // Get the output text
  var avatar = document.getElementById("avatar");
  var picture = document.getElementById("picture");

  // If the checkbox is checked, display the output text
  if (picture.style.display == "none"){
    var result = confirm("You are going to display an original picture. It raises privacy issues. Are you sure?");
    if(!result){
      return
    }
    picture.style.display = "block";
    avatar.style.display = "none"
    buttonPicture.textContent = "Show avatar"
  } else {
    avatar.style.display = "block";
    picture.style.display = "none"
    buttonPicture.textContent = "Show picture"
  }
} 