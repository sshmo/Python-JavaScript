document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelector("#inbox")
    .addEventListener("click", () => load_mailbox("inbox"));
  document
    .querySelector("#sent")
    .addEventListener("click", () => load_mailbox("sent"));
  document
    .querySelector("#archived")
    .addEventListener("click", () => load_mailbox("archive"));
  document.querySelector("#compose").addEventListener("click", compose_email);

  // By default, load the inbox
  load_mailbox("inbox");
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  document
    .querySelector("#compose-form")
    .addEventListener("submit", (event) => {
      var recip = document.querySelector("#compose-recipients").value;
      var subj = document.querySelector("#compose-subject").value;
      var bod = document.querySelector("#compose-body").value;

      fetch("/emails", {
        method: "POST",
        body: JSON.stringify({
          recipients: recip,
          subject: subj,
          body: bod,
        }),
      })
        .then((response) => response.json())
        .then((result) => {
          // Print result
          console.log(result);
        });

      // Clear out composition fields
      document.querySelector("#compose-recipients").value = "";
      document.querySelector("#compose-subject").value = "";
      document.querySelector("#compose-body").value = "";

      //load the sent box
      load_mailbox("sent");

      event.preventDefault();
    });
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector("#emails-view").innerHTML = "";
  document.querySelector("#emails-view").style.display = "block";
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "none";

  const container = document.createElement("div");
  container.className = "container mx-auto";

  // Show the mailbox name
  container.innerHTML = `<h3>${
    mailbox.charAt(0).toUpperCase() + mailbox.slice(1)
  }</h3>`;

  // Show the emails
  fetch("/emails/" + mailbox)
    .then((response) => response.json())
    .then((emails) => {
      emails.forEach((email) => {
        const row = document.createElement("div");

        row.className = `row border rounded my-1 align-text-middle text-dark`;

        const bgc = !email["read"]
          ? " background-color: white;"
          : " background-color: #E8E8E8;";
        row.style = `width:80%; ${bgc};`;

        container.appendChild(row);

        // Add click listener to each email
        row.addEventListener("click", function () {
          load_email(email["id"]);
        });

        const col_1 = document.createElement("div");
        col_1.className = "col";
        row.appendChild(col_1);
        col_1.innerHTML = `From: ${email["sender"]}`;

        const col_2 = document.createElement("div");
        row.appendChild(col_2);
        col_2.className = "col";
        col_2.innerHTML = `Subject: ${email["subject"]}`;

        const col_3 = document.createElement("div");
        row.appendChild(col_3);
        col_3.className = "col";
        col_3.innerHTML = `${email["timestamp"]}`;
      });
      document.querySelector("#emails-view").append(container);
    });
}

function load_email(email_id) {
  // Show the email and hide other views
  document.querySelector("#compose-view").style.display = "none";
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#email-view").innerHTML = "";
  document.querySelector("#email-view").style.display = "block";

  // Mark email as read
  fetch(`/emails/${email_id}`, {
    method: "PUT",
    body: JSON.stringify({
      read: true,
    }),
  });
      
  const container = document.createElement("div");
  container.className = "container w-75";

  // Show the email
  fetch(`/emails/${email_id}`)
    .then((response) => response.json())
    .then((email) => {
      
      const row_1 = document.createElement("div");
      row_1.className = `row border rounded my-1 align-text-middle text-dark`;
      container.appendChild(row_1);

      const col_1_1 = document.createElement("div");
      col_1_1.className = "col";
      row_1.appendChild(col_1_1);
      col_1_1.innerHTML = `Subject: ${email["subject"]}`;

      const row_2 = document.createElement("div");
      row_2.className = `row border rounded my-1 align-text-middle text-dark`;
      container.appendChild(row_2);

      const col_2_1 = document.createElement("div");
      col_2_1.className = "col";
      row_2.appendChild(col_2_1);
      col_2_1.innerHTML = `From: ${email["sender"]}`;

      const col_2_2 = document.createElement("div");
      col_2_2.className = "col";
      row_2.appendChild(col_2_2);
      col_2_2.innerHTML = `To: ${email["recipients"]}`;

      const col_2_3 = document.createElement("div");
      col_2_3.className = "col";
      row_2.appendChild(col_2_3);
      col_2_3.innerHTML = `On: ${email["timestamp"]}`;


      const row_3 = document.createElement("div");
      row_3.className = `row border rounded my-1 align-text-middle text-dark`;
      container.appendChild(row_3);

      const col_3_1 = document.createElement("div");
      col_3_1.className = "col h-100px";
      row_3.appendChild(col_3_1);
      col_3_1.innerHTML = `${email["body"]}`;


      document.querySelector("#email-view").append(container);
    });
}
