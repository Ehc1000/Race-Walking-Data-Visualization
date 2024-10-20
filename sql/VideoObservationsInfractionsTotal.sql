SELECT COUNT(BibNumber) AS NbrInfractions, "<" AS Infraction FROM (SELECT BibNumber
FROM VideoObservation 
WHERE IDRace=? AND KneeAngle > 0 AND KneeAngle <=175
GROUP BY BibNumber
HAVING COUNT(BibNumber) > 1)
UNION
SELECT COUNT(BibNumber) AS NbrInfractions, "~" AS Infraction FROM (SELECT BibNumber, ROUND(AVG(LOCAverage),1) AS LOCAverage 
FROM VideoObservation WHERE IDRace = ? AND LOCAverage >=60
GROUP BY BibNumber
HAVING COUNT(BibNumber)>=2)
