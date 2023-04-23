// Note: requires manually setting target folder and creating an array of JSON files' names from folder

async function loadCharts() {
    const targetFolder = "charts/exp6_gov/";
    const fileList = await fetch("file_list.json").then((response) => response.json());
  
    const container = document.querySelector(".container");
  
    fileList.forEach((fileName) => {
      const chartDiv = document.createElement("div");
      chartDiv.className = "chart";
      const cardDiv = document.createElement("div");
      cardDiv.className = "card";
      cardDiv.appendChild(chartDiv);
      container.appendChild(cardDiv);
  
      const chartPath = targetFolder + fileName;
      vegaEmbed(chartDiv, chartPath, { "actions": true });
    });
  }
  
  loadCharts();
  