SELECT Athlete.IDAThlete, LOCData.BibNumber, ROUND(AVG(LOCData.LOCAverage),1) AS LOCAverage, COUNT(LOCData.BibNumber) As NbrMeasurements, Athlete.LastName, Athlete.FirstName FROM (
SELECT IDAthlete, BibNumber, LOCAverage, RANK() OVER (Partition by BibNumber Order by LOCAverage DESC) LOCRank FROM VideoObservation WHERE IDRace = 6) LOCData
INNER JOIN Athlete ON Athlete.IDAthlete=LOCData.IDAthlete
WHERE LOCData.LOCRank < 3 AND LOCData.LOCAverage >=50
GROUP BY LOCData.BibNumber
HAVING LOCData.LOCAverage >= 50 AND COUNT(LOCData.BibNumber)>=2
ORDER BY ROUND(AVG(LOCData.LOCAverage),1) DESC
