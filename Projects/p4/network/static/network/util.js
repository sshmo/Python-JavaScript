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
    edit_btn.className = "btn btn-outline-primary ml-auto"
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

function like(ids) {

    ids = ids.split(",")
    var post_id = parseInt(ids[0])
    var user_id = parseInt(ids[1])

    var likes =  parseInt(document.getElementById(`likes${post_id}`).innerHTML)

    // get the post likers
    fetch(`/posts/${post_id}`)
    .then((response) => response.json())
    .then((post) => {
        
        var likers = post["likers"]
        var liked = false
        var baseURL = "http://127.0.0.1:8000/static/network/"
    
        // add or remove liker
        if (!likers.includes(user_id)) {
            liked = true
            likes += 1
            document.getElementById(`like${post_id}`).src = baseURL + 'like1.png'
        }
        else {
            likes -=1
            document.getElementById(`like${post_id}`).src = baseURL + 'like.png'
        }

        document.getElementById(`likes${post_id}`).innerHTML = likes

        // Save post in database
        fetch(`/posts/${post_id}`, {
            method: "PUT",
            body: JSON.stringify({
                liked: liked,
                user: user_id,
            }),
        });
    })
}
