document.addEventListener("DOMContentLoaded", function () {
});

function edit(post_id) {
    
    edit_btn = document.getElementById(`edit${post_id}`)
    post = document.getElementById(`post${post_id}`)

    var textarea_node = document.createElement(tagName='textarea')
    textarea_node.id = `text${post_id}`
    textarea_node.className = "form-control"
    textarea_node.value = post.innerHTML
    post.innerText = ""
    post.appendChild(textarea_node)

    var save_btn = document.createElement(tagName='button')
    save_btn.innerText = "Save"
    save_btn.className = "btn btn-primary ml-auto"
    save_btn.id = `save${post_id}`
    save_btn.addEventListener("click", ()=>{
        save(post_id)
    })
    edit_btn.parentNode.appendChild(save_btn)
    edit_btn.parentNode.removeChild(edit_btn)
    
}

function save(post_id) {
    textarea_node = document.getElementById(`text${post_id}`)
    post_content = textarea_node.value
    
    post = document.getElementById(`post${post_id}`)
    post.innerHTML = post_content

    save_btn = document.getElementById(`save${post_id}`)
    var edit_btn = document.createElement(tagName='button')
    edit_btn.innerText = "Edit"
    edit_btn.className = "btn btn-primary ml-auto"
    edit_btn.id = `edit${post_id}`
    edit_btn.addEventListener("click", ()=>{
        edit(post_id)
    })
    save_btn.parentNode.appendChild(edit_btn)
    save_btn.parentNode.removeChild(save_btn)

    // Save post in database
    fetch(`/posts/${post_id}`, {
        method: "PUT",
        body: JSON.stringify({
        edit: post_content,
        }),
    });
}

