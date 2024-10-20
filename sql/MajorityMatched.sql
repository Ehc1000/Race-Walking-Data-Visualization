Select Judge.FirstName, Judge.LastName, 
max(case When Infraction='~' AND Color='Red' THEN MajorityNumber Else 0 END) MajorityMatchedLOCRed,
max(case When Infraction='<' AND Color='Red' THEN MajorityNumber Else 0 END) MajorityMatchedBentRed,
max(case When Infraction='~' AND Color='Yellow' THEN MajorityNumber Else 0 END) MajorityMatchedLOCYellow,
max(case When Infraction='<' AND Color='Yellow' THEN MajorityNumber Else 0 END) MajorityMatchedBentYellow
FROM
(SELECT JudgeCall.IDJudge, Count(JudgeCall.BibNumber) as MajorityNumber, JudgeCall.Infraction, JudgeCall.Color
FROM JudgeCall INNER JOIN
(SELECT JudgeCall.BibNumber, JudgeCall.IDRace, JudgeCall.Color, JudgeCall.Infraction
FROM JudgeCall 
WHERE JudgeCall.IDRace = ?
GROUP BY JudgeCall.BibNumber, JudgeCall.IDRace, JudgeCall.Color, JudgeCall.Infraction
HAVING (Count(JudgeCall.Infraction))>=(Select COUNT(IDJudge)/2 from RaceJudge WHERE RaceJudge.IDRace=?)) MajorityCallPerAthlete 
ON (JudgeCall.Infraction = MajorityCallPerAthlete.Infraction) AND 
(JudgeCall.Color = MajorityCallPerAthlete.Color) AND (JudgeCall.BibNumber = MajorityCallPerAthlete.BibNumber) AND 
(JudgeCall.IDRace = MajorityCallPerAthlete.IDRace)
GROUP BY JudgeCall.IDJudge, JudgeCall.Color, JudgeCall.Infraction) MajorityCallByJudge
LEFT JOIN Judge ON Judge.IDJudge=MajorityCallByJudge.IDJudge
GROUP BY MajorityCallByJudge.IDJudge
ORDER BY Judge.LastName, Judge.FirstName
