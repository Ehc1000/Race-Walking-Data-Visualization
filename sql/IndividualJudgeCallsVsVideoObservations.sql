SELECT J.FirstName, J.LastName, JC.BibNumber, A.FirstName, A.LastName, JC.Infraction, IFNULL(VideoLOC.LOCAverage, "-") AS LOC, IFNULL(VideoBent.AverageKneeBend, "-") as KneeAngle,
CASE  
    WHEN Infraction = "~" AND VideoLOC.LOCAverage >= ? THEN 'CORRECT'
    WHEN Infraction = "~" AND VideoLOC.LOCAverage < ? THEN 'X'
    WHEN Infraction = "<" AND VideoBent.AverageKneeBend > ? AND VideoBent.AverageKneeBend <= ? THEN 'CORRECT'
    ELSE 'X'
END Correctness
FROM JudgeCall JC INNER JOIN Judge J ON JC.IDJudge=J.IDJudge
INNER JOIN Bib B ON B.BibNumber = JC.BibNumber
INNER JOIN Athlete A ON A.IDAthlete = B.IDAthlete
LEFT JOIN 
(SELECT Athlete.IDAThlete, LOCData.BibNumber, ROUND(AVG(LOCData.LOCAverage),1) AS LOCAverage, COUNT(LOCData.BibNumber) As NbrMeasurements, Athlete.LastName, Athlete.FirstName FROM (
SELECT IDAthlete, BibNumber, LOCAverage, RANK() OVER (Partition by BibNumber Order by LOCAverage DESC) LOCRank FROM VideoObservation WHERE IDRace = ?) LOCData
INNER JOIN Athlete ON Athlete.IDAthlete=LOCData.IDAthlete
WHERE LOCData.LOCRank < ? AND LOCData.LOCAverage >=?
GROUP BY LOCData.BibNumber
HAVING LOCData.LOCAverage >= ? AND COUNT(LOCData.BibNumber)>=2) VideoLOC
ON VideoLOC.BibNumber = JC.BibNumber
LEFT JOIN
(SELECT Athlete.BibNumber, Round(avg(KneeAngle),1) as AverageKneeBend, COUNT(Athlete.BibNumber) AS NbrMeasurements, Athlete.FirstName, Athlete.LastName
FROM VideoObservation INNER JOIN Athlete ON VideoObservation.IDAthlete =Athlete.IDAthlete
WHERE IDRace=? AND KneeAngle > ? AND KneeAngle <=?
GROUP BY Athlete.BibNumber
HAVING COUNT(Athlete.BibNumber) > 1) VideoBent
ON VideoBent.BibNumber = JC.BibNumber

WHERE JC.IDRace=? AND JC.Color="Red"
ORDER BY J.LastName, J.FirstName, A.LastName, A.FirstName, JC.Infraction