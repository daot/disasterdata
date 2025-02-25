export const fetchWordData = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/fetch-most-frequent-word/");
      const data = await response.json();
  
      if (data && Array.isArray(data["count of each word"])) {
        return data["count of each word"].map(([text, value]) => ({
          text,
          value,
        }));
      } else {
        console.error("Unexpected API response format:", data);
        return [];
      }
    } catch (error) {
      console.error("Error fetching word cloud data:", error);
      return [];
    }
  };
  