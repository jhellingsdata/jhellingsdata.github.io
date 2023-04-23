/* automatically embed charts located within GitHub repository folder into html divs, ignores files starting with 'test', 
GitHub API rate limited to 60 requests per hour */

async function loadCharts() {
  const container = document.querySelector(".container");
  const targetFolder = container.dataset.targetFolder;

  const repoOwner = "jhellingsdata";
  const repoName = "jhellingsdata.github.io";
  const repoBranch = "main"; // or "master", depending on default branch

  const fileList = await fetch(
    `https://api.github.com/repos/${repoOwner}/${repoName}/contents/${targetFolder}?ref=${repoBranch}`
  ).then((response) => response.json());

  fileList.forEach((file) => {
    if (file.name.endsWith(".json") && !file.name.startsWith("test")) {
      const chartDiv = document.createElement("div");
      chartDiv.className = "chart";
      const cardDiv = document.createElement("div");
      cardDiv.className = "card";
      cardDiv.appendChild(chartDiv);
      container.appendChild(cardDiv);

      const chartPath = targetFolder + file.name;
      vegaEmbed(chartDiv, chartPath, { "actions": true });
    }
  });
}

loadCharts();
    
  