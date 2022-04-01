function hello() {
    if (document.querySelector('#hello').innerHTML==='Hellooooo') {
    document.querySelector('#hello').innerHTML='Goodbyeeeee';
    }
    else {
        document.querySelector('#hello').innerHTML='Hellooooo'
    }
}

// counter section
let counter = 0;
function count() {
    counter += 1;
    document.querySelector('span').innerHTML=counter;

    if (counter % 10 === 0) {
        alert(`Count is now ${counter}`)
    }
}

document.querySelector('form').onsubmit = () => {
    const name = document.querySelector('#name').value;
    alert(`Hello, ${name}`);
}

// document.querySelectorAll('.colotbtn').forEach((button) => {
//     button.onclick = ()=>{
//         document.querySelector('#yoyo').style.color = button.dataset.color;
//     }
// })

// document.addEventListener('DOMContentLoaded',() => {
//     document.querySelectorAll('.colotbtn').forEach((button) => {
//         button.onclick = ()=>{
//             document.querySelector('#yoyo').style.color = button.dataset.color;
//         }
//     })
// Change font color to red
document.querySelector('#red').onclick = () => {
    document.querySelector('#yoyo').style.color = document.querySelector('#red').dataset.color;
}

// Change font color to blue
document.querySelector('#blue').onclick = () => {
    document.querySelector('#yoyo').style.color = document.querySelector('#blue').dataset.color;
}

// Change font color to green
document.querySelector('#green').onclick = () => {
    document.querySelector('#yoyo').style.color = 'green';
}


// document.addEventListener('DOMContentLoaded',() => {
//     document.querySelector('select').onchange = function() {
//         document.querySelector('#yoyomama').style.color = this.value;
//     }
// });

document.querySelector('select').onchange = function() {
    document.querySelector('#yoyomama').style.color = this.value;
}