SELECT JudgeCall.BibNumber, A.FirstName, A.LastName, JudgeCall.Infraction, Judge.LastName As JudgeLastName, Judge.FirstName AS JudgeFirstName, A.CountryCode
FROM JudgeCall INNER JOIN Bib B ON JudgeCall.BibNumber=B.BibNumber AND JudgeCall.IDRace=B.IDRace
INNER JOIN Athlete A ON A.IDAthlete = B.IDAthlete 
INNER JOIN Judge ON Judge.IDJudge=JudgeCall.IDJudge
WHERE Color="Red" AND JudgeCall.IDRace = ? AND JudgeCall.BibNumber IN
(SELECT JC.BibNumber FROM JudgeCall JC
WHERE JC.Color = "Red" AND JC.IDRace=? and JC.BibNumber NOT IN 
    (SELECT VO.BibNumber FROM VideoObservation VO WHERE BentKneeAngle > ? AND BentKneeAngle <= ? AND VO.IDRace=?
     GROUP BY VO.BibNumber HAVING COUNT(VO.BibNumber) >= 2
     UNION
     SELECT BibNumber FROM VideoObservation VO WHERE VO.LOCAverage >= ? AND VO.IDRace=?
     GROUP BY VO.BibNumber
     HAVING COUNT(BibNumber) >= 2)
GROUP BY JC.BibNumber
HAVING COUNT(JC.BibNumber) >= 3)
ORDER BY A.LastName, A.FirstName, JudgeLastName, JudgeFirstName
