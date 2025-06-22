document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
  
    const response = await fetch("http://localhost:8080/api/accounts/login/", {
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
      document.getElementById("loginError").innerText = data.detail || "Login failed";
    }
  });
  