let searchWords=['WR','CS','AH','LY','LC','LF','LG','LH','LI','LK','LN','LP','AA','LX','BI','CH','PY','EE','BB','MS','MA','AN','SO','EC','PL','PS','IS','PH','RN','CL','HU','MU','TH','CI','EI','ME','CC']

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
