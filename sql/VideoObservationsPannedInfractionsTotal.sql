SELECT COUNT(BibNumber) AS NbrInfractions, "<" AS Infraction FROM (SELECT BibNumber
FROM VideoObservationPanned 
WHERE IDRace=6 AND KneeAngle > 0 AND KneeAngle <=175
GROUP BY BibNumber
HAVING COUNT(BibNumber) > 1)
UNION
SELECT COUNT(BibNumber) AS NbrInfractions, "~" AS Infraction FROM (SELECT BibNumber, ROUND(AVG(LOCAverage),1) AS LOCAverage 
FROM VideoObservationPanned WHERE IDRace = 6 AND LOCAverage >=60
GROUP BY BibNumber
HAVING COUNT(BibNumber)>=2)
