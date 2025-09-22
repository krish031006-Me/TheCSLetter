/* The purpose of this file is to act as our own js file for this project*/

let typingTimeout = null;
let typingId = 0;
// using local storage to set global mode
let mode = localStorage.getItem('mode') || "dark";
// calling the typing function when all content is loaded
document.addEventListener("DOMContentLoaded", function (event){    
    title_bar();
    type();
    dark(mode);
});

// the type function-
function type(){
    // Only run on dashboard.html (where #title exists)
    if (document.getElementById("title")) {

        // checking if there is already an animation running
        if (typingTimeout){
            clearTimeout(typingTimeout);
            typingTimeout = null;
        }
        typingId++;
        const myrun = typingId;
        // text is an array storing all the letters in groups
        let text = ["The", "C", "S", "Letter"];
        // getting the whole title element 
        let spans = [
            document.getElementById("span1"),
            document.getElementById("span2"),
            document.getElementById("span3"),
            document.getElementById("span4"),
        ];
        if (!spans[0] || !spans[1] || !spans[2] || !spans[3]){
            return;
        }
        
        // Making sure the spans are clear-
        for(let i = 0; i < spans.length; i++){
            spans[i].innerHTML = "";
        }
        // Two counters one for word and one for letters
        let word_count = 0, letter_count = 0;
        // the fucntion for typing
        function type_title(){
            if(myrun != typingId){
                typingTimeout = null;
                return;
            }
            // creating a return statement
            if (word_count >= text.length){
                typingTimeout = null;
                return;
            }
            // choosing the colors
            if (mode === "light"){
                spans[0].style.setProperty('color', '#ffffff', 'important');
                spans[3].style.setProperty('color', '#ffffff', 'important');
            }
            else{
                spans[0].style.setProperty('color', '#353839', 'important');
                spans[3].style.setProperty('color', '#353839', 'important');
            }
            // adding one letter
            if (letter_count < text[word_count].length){
                spans[word_count].innerHTML += text[word_count][letter_count];
                letter_count++;
            }
            else{
                word_count++;
                letter_count = 0;
            }
            typingTimeout = setTimeout(type_title, 100);
        }
        // caling the typing function
        type_title();
    }
}
// THis function is used to change the variable mode-
function toggle(){
    // toggling the mode
    if (mode == 'light'){
        mode = 'dark';
    }
    else{
        mode = 'light';
    }
    // setting it in the localstorage
    localStorage.setItem('mode', mode);
    type();
    dark(mode);
}

// This is the dark function used to change between dark and light modes
function dark(mode){
    title_bar();
    // getting the label
    let label = document.getElementById("btn_label")
    // getting the img inside the button by using querSelector only 
    let img = document.querySelector("#mode_button img");
    let bar = document.getElementById("title_bar");
    const slides = document.querySelectorAll(".carousel-item");
    // chekcing is any element is empty-
    if (!label || !img || !bar){
        return;
    }
    let body = document.body;
    let button = document.getElementById("mode_button")
    // getting all elements with distinct_text and subscribe_text class and storing them in a HTMLCollection format which is like a array
    let distinct = document.getElementsByClassName("distinct_text");
    let subscribe = document.getElementsByClassName("subscribe_text");
    // cheking for mode and changing colors
    if (mode === "dark"){
        body.style.backgroundColor = "#d0e8ff";
        bar.style.backgroundColor = "#a6d1ff";
        body.style.setProperty('color', '#2c2c2c', 'important');
        bar.style.setProperty('color', '#2c2c2c', 'important');
        // changing the background color of button
        button.style.setProperty('background-color', '#CBE4FF');
        slides.forEach(slide => {
            slide.style.setProperty('background-color', 'rgba(0, 0, 0, 0.3)');
        });
        // for loop to change their colors-
        for(let i = 0; i < distinct.length; i++){
            distinct[i].style.setProperty('color', '#1E3A8A', 'important');
        }
        for(let j = 0; j < subscribe.length; j++){
            subscribe[j].style.setProperty('color', '#FF3B30', 'important');
        }
        // changes in image inside button
        img.src = "/static/finalmoon.png";
        //changing the label
        label.innerHTML = "Dark Mode";
    }
    else{
        body.style.backgroundColor = "#121212";
        bar.style.backgroundColor = "#1F1F1F";
        body.style.setProperty('color', '#E6E6E6', 'important');
        bar.style.setProperty('color', '#E6E6E6', 'important');
        button.style.setProperty('background-color', '#4A4A4A');
        slides.forEach(slide => {
            slide.style.setProperty('background-color', 'rgba(255, 255, 255, 0.15)');
        });
        for(let i = 0; i < distinct.length; i++){
            distinct[i].style.setProperty('color', '#58A6FF', 'important');
        }
        for(let j = 0; j < subscribe.length; j++){
            subscribe[j].style.setProperty('color', 'lightgreen', 'important');
        }
        // it will change the image 
        img.src = "/static/finalsun.png";
        // changing the label
        label.innerHTML = "Light Mode";
    }
}   

// function for title_bar colors:
function title_bar(){
    // getting the two same color words in title
    let title_word = [
        document.getElementById("first_text"),
        document.getElementById("second_text")
    ];
    // setting the colors for the tile_word
    title_word.forEach(word => {
        if (word){
            if (mode === 'light'){
                word.style.setProperty('color', '#ffffff');
            }
            else{
                word.style.setProperty('color', '#2c2c2c');
            }
        }
    });
    return;
}