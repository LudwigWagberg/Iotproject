SELECT 
    DATE(`date`) AS `day`,
    AVG(`temperature`) AS `avg_temperature`
FROM 
    `sensor_data`
WHERE 
    `date` >= CURDATE() - INTERVAL 5 DAY
    AND `date` < CURDATE()
GROUP BY 
    `day`
ORDER BY 
    `day` DESC;
