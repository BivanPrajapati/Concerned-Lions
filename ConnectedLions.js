let searchWords=['AA','AR','AM','CS','DS','WR']

const resultsBox=document.querySelector(".result-box");
const inputsBox=document.getElementById("input-box");

inputsBox.onkeyup=function(){
    let results=[];
    let input= inputsBox.value;
    if(input.length){
        result=searchWords.filter((keyword)=>{
            return keyword.toLowerCase().includes(input.toLowerCase());
        });
    }
    display(result);
}

function display(result){
    const content= result.map((list)=>{ return "<li>"+list+"<li>"; });

    resultsBox.innerHTML="<ul>"+content+"</ul>";
}
