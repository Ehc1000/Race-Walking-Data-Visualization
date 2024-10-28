SELECT FinalXRedLOC.LastName, FinalXRedLOC.FirstName, 
   IFNULL(FinalXRedLOC.XRedLOC,0) AS XRedLOC, IFNULL(FinalMatchLOC.CorRedLOC, 0) AS CorRedLOC,
   IFNULL(FinalXRedBent.XRedBent,0) AS XRedBent, IFNULL(FinalMatchBent.CorRedBent, 0) AS CorRedBent,
   IFNULL(FinalMissing.MissedLOCRed, 0) AS MissedLOCRed, IFNULL(FinalMissing.MissedBentRed,0) AS MissedBentRed,  
   IFNULL(FinalNoCalls.NbrCorrectNonCalls, 0) AS NbrCorrectNonCalls,
   IFNULL(FinalDiscrepancy.NbrDiscrepancies,0) AS NbrDiscrepancies,  
   IFNULL(FinalMatchLOC.CorRedLOC, 0)*2 + IFNULL(FinalMatchBent.CorRedBent, 0)*2 
   + IFNULL(FinalNoCalls.NbrCorrectNonCalls, 0)*.5 
   - IFNULL(FinalXRedLOC.XRedLOC,0) - IFNULL(FinalXRedBent.XRedBent,0)
   - IFNULL(FinalMissing.MissedLOCRed,0)*2 - IFNULL(FinalMissing.MissedBentRed,0)*2 - 
 IFNULL(FinalDiscrepancy.NbrDiscrepancies,0) AS Score
FROM

--- Excessive Red Cards for LOC
(SELECT Judge.FirstName, Judge.LastName, JC.IDJudge, COUNT(JC.BibNumber ) AS XRedLOC
FROM JudgeCall JC INNER JOIN Judge ON JC.IDJudge = Judge.IDJudge  
WHERE JC.Color = "Red" AND Infraction="~" AND JC.IDRace=?
AND JC.BibNumber NOT IN 
(SELECT BibNumber FROM VideoObservation VO WHERE VO.LOCAverage >= ? AND VO.IDRace=?
GROUP BY VO.BibNumber
HAVING COUNT(VO.BibNumber) > 1)
GROUP BY JC.IDJudge
ORDER BY Judge.LastName, Judge.FirstName) FinalXRedLOC

LEFT JOIN 

--- Excessive Red Cards for Bent
(SELECT Judge.FirstName, Judge.LastName, JC.IDJudge, COUNT(JC.BibNumber ) AS XRedBent
FROM JudgeCall JC INNER JOIN Judge ON JC.IDJudge = Judge.IDJudge  
WHERE JC.Color = "Red" AND Infraction="<" AND JC.IDRace=?
AND JC.BibNumber NOT IN 
        (SELECT VO.BibNumber FROM VideoObservation VO WHERE KneeAngle > ? AND KneeAngle <= ? AND VO.IDRace=?
     GROUP BY VO.BibNumber HAVING COUNT(VO.BibNumber) > 1)      
GROUP BY JC.IDJudge
ORDER BY Judge.LastName, Judge.FirstName) FinalXRedBent
ON FinalXRedLOC.IDJudge=FinalXRedBent.IDJudge

LEFT JOIN 

---Judges Matching the LOC Video Observations
(SELECT J.FirstName, J.LastName, J.IDJudge, COUNT(BibNumber) AS CorRedLOC FROM Judge J INNER JOIN 
(SELECT JC.IDJudge, JC.BibNumber FROM JudgeCall JC WHERE JC.IDRace=? AND JC.Color="Red" AND JC.Infraction="~" AND JC.BibNumber IN
(SELECT BibNumber FROM VideoObservation VO WHERE VO.LOCAverage >= ? AND VO.IDRace=?
GROUP BY VO.BibNumber
HAVING COUNT(VO.BibNumber) > 1)) InnerDetails ON J.IDJudge=InnerDetails.IDJudge
GROUP BY InnerDetails.IDJudge
ORDER By J.LastName, J.FirstName) FinalMatchLOC
ON FinalXRedLOC.IDJudge=FinalMatchLOC.IDJudge

LEFT JOIN 

---Judges Matching the Bent Knee Video Observations
(SELECT J.FirstName, J.LastName, J.IDJudge, COUNT(BibNumber) AS CorRedBent FROM Judge J INNER JOIN 
(SELECT JC.IDJudge, JC.BibNumber FROM JudgeCall JC WHERE JC.IDRace=? AND JC.Color="Red" AND JC.Infraction="<" AND JC.BibNumber IN
(SELECT VO.BibNumber FROM VideoObservation VO WHERE KneeAngle > ? AND KneeAngle <= ? AND VO.IDRace=?
     GROUP BY VO.BibNumber HAVING COUNT(VO.BibNumber) > 1)) InnerDetails ON J.IDJudge=InnerDetails.IDJudge
GROUP BY InnerDetails.IDJudge
ORDER By J.LastName, J.FirstName) FinalMatchBent
ON FinalXRedLOC.IDJudge=FinalMatchBent.IDJudge

LEFT JOIN 


--- Judges Missing Red Cards from the Video Observations 
(SELECT Judge.FirstName, Judge.LastName, Judge.IDJudge,
MAX(CASE WHEN Infraction='~' AND Color='Red' THEN MissedNumber ELSE 0 END) MissedLOCRed,
MAX(CASE WHEN Infraction='<' AND Color='Red' THEN MissedNumber ELSE 0 END) MissedBentRed
FROM (SELECT IDJudge, COUNT(BibNumber) AS MissedNumber, Color, Infraction
FROM (SELECT RaceJudge.IDJudge, CorrectCalls.BibNumber, CorrectCalls.Color, CorrectCalls.Infraction
FROM (SELECT VO.BibNumber, VO.IDRace, "Red" AS Color, "<" AS Infraction FROM VideoObservation VO 
WHERE KneeAngle > ? AND KneeAngle <= ? AND VO.IDRace=?
     GROUP BY VO.BibNumber HAVING COUNT(VO.BibNumber) > 1
     UNION
SELECT BibNumber, VO.IDRace, "Red" AS Color, "~" AS Infraction FROM VideoObservation VO 
WHERE VO.LOCAverage >= ? AND VO.IDRace=?
GROUP BY VO.BibNumber
HAVING COUNT(VO.BibNumber) > 1) CorrectCalls, RaceJudge
WHERE RaceJudge.IDRace=?
EXCEPT
SELECT IDJudge, BibNumber, Color, Infraction FROM JudgeCall WHERE IDRace=?)
GROUP BY IDJudge, Color, Infraction) MissedCalls
LEFT JOIN Judge ON Judge.IDJudge = MissedCalls.IDJudge
GROUP BY MissedCalls.IDJudge
ORDER BY Judge.LastName, Judge.FirstName) FinalMissing

ON FinalXRedLOC.IDJudge=FinalMissing.IDJudge

LEFT JOIN 

---Judges Discrepancy from the Video Observations 
(SELECT Judge.IDJudge, COUNT(Discrepancies.BibNumber) AS NbrDiscrepancies, Judge.FirstName, Judge.LastName FROM 
(SELECT ActualJudgeCalls.IDJudge, ActualJudgeCalls.BibNumber
FROM (

SELECT RaceJudge.IDJudge, CorrectCalls.BibNumber, CorrectCalls.Color, CorrectCalls.Infraction FROM 
(SELECT VO.BibNumber, VO.IDRace, "Red" AS Color, "<" AS Infraction FROM VideoObservation VO 
WHERE KneeAngle > ? AND KneeAngle <= ? AND VO.IDRace=?
     GROUP BY VO.BibNumber HAVING COUNT(VO.BibNumber) > 1
     UNION
SELECT BibNumber, VO.IDRace, "Red" AS Color, "~" AS Infraction FROM VideoObservation VO 
WHERE VO.LOCAverage >= ? AND VO.IDRace=?
GROUP BY VO.BibNumber
HAVING COUNT(VO.BibNumber) > 1) CorrectCalls, RaceJudge
WHERE RaceJudge.IDRace=?) VideoCalls
INNER JOIN 
(SELECT IDJudge, BibNumber, Color, Infraction FROM JudgeCall  WHERE IDRace=? AND Color="Red") ActualJudgeCalls 
ON VideoCalls.BibNumber=ActualJudgeCalls.BibNumber 
WHERE ActualJudgeCalls.Infraction <> VideoCalls.Infraction
GROUP BY ActualJudgeCalls.IDJudge, ActualJudgeCalls.BibNumber) Discrepancies INNER JOIN Judge ON Discrepancies.IDJudge=Judge.IDJudge
GROUP BY Judge.IDJudge
ORDER BY Judge.LastName, Judge.FirstName) FinalDiscrepancy

ON FinalXRedLOC.IDJudge=FinalDiscrepancy.IDJudge

LEFT JOIN

-- Judge Non calls from the Video Observations
(SELECT J.FirstName, J.LastName, AllJudgesAllBib.IDJudge,Count(AllJudgesAllBib.BibNumber) AS NbrCorrectNonCalls FROM
(SELECT BibNumber, IDJudge FROM Bib, RaceJudge WHERE Bib.IDRace=? AND RaceJudge.IDRace=?) AllJudgesAllBib
INNER JOIN Judge J ON J.IDJudge=AllJudgesAllBib.IDJudge
LEFT JOIN
(SELECT BibNumber,IDJudge FROM JudgeCall WHERE IDRace=? AND Color="Red") JudgeCalls
ON AllJudgesAllBib.IDJudge=JudgeCalls.IDJudge AND AllJudgesAllBib.BibNumber=JudgeCalls.BibNumber
WHERE JudgeCalls.IDJudge IS NULL AND AllJudgesAllBib.BibNumber IN
---Bibs of legal walkers in a race 
(SELECT BibNumber FROM BIB WHERE IDRace=? AND 
BibNumber NOT IN (
SELECT VO.BibNumber FROM VideoObservation VO 
WHERE KneeAngle > ? AND KneeAngle <= ? AND VO.IDRace=?
     GROUP BY VO.BibNumber HAVING COUNT(VO.BibNumber) > 1
     UNION
SELECT BibNumber FROM VideoObservation VO 
WHERE VO.LOCAverage >= ? AND VO.IDRace=?
GROUP BY VO.BibNumber
HAVING COUNT(VO.BibNumber) > 1))
GROUP BY AllJudgesAllBib.IDJudge) FinalNoCalls

ON FinalXRedLOC.IDJudge=FinalNoCalls.IDJudge

ORDER BY Score DESC