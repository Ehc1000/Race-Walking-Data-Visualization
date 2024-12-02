SELECT Athlete.BibNumber,
       Round(avg(LOCAverage), 1) as Average,
       COUNT(Athlete.BibNumber)  AS NbrMeasurements,
       Athlete.FirstName,
       Athlete.LastName
FROM VideoObservation
         INNER JOIN Athlete ON VideoObservation.IDAthlete = Athlete.IDAthlete
WHERE IDRace = :race_id
GROUP BY Athlete.BibNumber
ORDER BY AVERAGE DESC;
