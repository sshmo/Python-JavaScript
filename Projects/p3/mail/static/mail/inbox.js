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

function compose_email(context) {
  // Show compose view and hide other views
  document.querySelector("#email-view").style.display = "none";
  document.querySelector("#emails-view").style.display = "none";
  document.querySelector("#compose-view").style.display = "block";

  // Pre fill the form if context was provided
  if (`${context}` != "[object MouseEvent]") {
    document.querySelector("#compose-recipients").value = context["recipient"];

    document.querySelector("#compose-subject").value = context["subject"];

    document.querySelector(
      "#compose-body"
    ).value = `On ${context["timestamp"]} ${context["recipient"]} wrote: \n\n ${context["body"]}`;
  }

  // Compose email when it is submitted
  document.querySelector("#compose-form").addEventListener("submit", () => {
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
    
    load_mailbox("sent");

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
          load_email(email["id"], mailbox);
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

function load_email(email_id, mailbox) {
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
  container.className = "container";

  // Show the email
  fetch(`/emails/${email_id}`)
    .then((response) => response.json())
    .then((email) => {
      const info = document.createElement("div");
      container.appendChild(info);
      info.innerHTML = `<b>Subject: </b>${email["subject"]}<br>
                        <b>From: </b>${email["sender"]}<br>
                        <b>To: </b>${email["recipients"]}<br>
                        <b>Timestamp: </b>${email["timestamp"]}`;

      if (mailbox != "sent") {
        const archive = document.createElement("button");
        archive.className = "btn btn-sm btn-outline-primary m";
        archive_str = email["archived"] ? "Unarchive" : "Archive";
        archive.innerHTML = archive_str;
        archive.addEventListener("click", function () {
          archive_email(email_id, archive_str);
        });
        container.appendChild(archive);
      }

      const reply = document.createElement("button");
      reply.className = "btn btn-sm btn-outline-primary m-2";
      reply.innerHTML = "Reply";
      reply.addEventListener("click", function () {
        subject_has_re =
          email["subject"].charAt(0) +
            email["subject"].charAt(1) +
            email["subject"].charAt(2) ===
          "Re:"
            ? true
            : false;

        context = {
          recipient: email["sender"],
          subject: subject_has_re ? email["subject"] : "Re:" + email["subject"],
          timestamp: email["timestamp"],
          body: email["body"],
        };

        compose_email(context);
      });
      container.appendChild(reply);

      const textarea = document.createElement("textarea");
      textarea.className = "col text-dark";
      textarea.setAttribute("disabled", "true");
      container.appendChild(textarea);
      textarea.innerHTML = `${email["body"]}`;

      document.querySelector("#email-view").append(container);
    });
}

async function archive_email(email_id, archive_str) {
  // Mark email as Archive
  fetch(`/emails/${email_id}`, {
    method: "PUT",
    body: JSON.stringify({
      archived: archive_str === "Archive" ? true : false,
    }),
  });
  await new Promise((r) => setTimeout(r, 50));
  load_mailbox("inbox");
}
