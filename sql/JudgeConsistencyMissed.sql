SELECT Judge.FirstName, Judge.LastName, 
MAX(CASE WHEN Infraction='~' AND Color='Red' THEN MissedNumber ELSE 0 END) MissedLOCRed,
MAX(CASE WHEN Infraction='<' AND Color='Red' THEN MissedNumber ELSE 0 END) MissedBentRed,
MAX(CASE WHEN Infraction='~' AND Color='Yellow' THEN MissedNumber ELSE 0 END) MissedLOCYellow,
MAX(CASE WHEN Infraction='<' AND Color='Yellow'THEN MissedNumber ELSE 0 END) MissedBentYellow
FROM (SELECT IDJudge, COUNT(BibNumber) AS MissedNumber, Color, Infraction
FROM (SELECT RaceJudge.IDJudge, MajorityCalls.BibNumber, MajorityCalls.Color, MajorityCalls.Infraction
FROM (SELECT JudgeCall.BibNumber, JudgeCall.IDRace, JudgeCall.Color, JudgeCall.Infraction
FROM JudgeCall 
WHERE JudgeCall.IDRace = 6
GROUP BY JudgeCall.BibNumber, JudgeCall.IDRace, JudgeCall.Color, JudgeCall.Infraction
HAVING (Count(JudgeCall.Infraction))>=(SELECT COUNT(IDJudge)/2 FROM RaceJudge WHERE RaceJudge.IDRace=6)) MajorityCalls, RaceJudge
WHERE RaceJudge.IDRace=6
EXCEPT
SELECT IDJudge, BibNumber, Color, Infraction FROM JudgeCall WHERE IDRace=6)
GROUP BY IDJudge, Color, Infraction) MissedCalls
LEFT JOIN Judge ON Judge.IDJudge = MissedCalls.IDJudge
GROUP BY MissedCalls.IDJudge
ORDER BY Judge.LastName, Judge.FirstName
