document.getElementById("signupForm").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const confirm = document.getElementById("confirm").value;
  
    if (password !== confirm) {
      document.getElementById("signupError").innerText = "Passwords do not match.";
      return;
    }
  
    try {
      const response = await fetch("http://localhost:8080/api/accounts/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ email, password })
      });
  
      const data = await response.json();
  
      if (response.ok && data.access) {
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
        window.location.href = "index.html";
      } else {
        document.getElementById("signupError").innerText =
          data.detail || JSON.stringify(data) || "Signup failed.";
      }
  
    } catch (err) {
      document.getElementById("signupError").innerText = "Something went wrong.";
      console.error(err);
    }
  });
  