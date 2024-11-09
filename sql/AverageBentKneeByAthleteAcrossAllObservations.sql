SELECT Athlete.BibNumber, Round(avg(KneeAngle),1) as AverageKneeBend, COUNT(Athlete.BibNumber) AS NbrMeasurements, Athlete.FirstName, Athlete.LastName
FROM VideoObservation INNER JOIN Athlete ON VideoObservation.IDAthlete =Athlete.IDAthlete
WHERE IDRace=? AND KneeAngle > ? AND KneeAngle <=?
GROUP BY Athlete.BibNumber
HAVING COUNT(Athlete.BibNumber) > 1
ORDER BY AverageKneeBend ASC;
