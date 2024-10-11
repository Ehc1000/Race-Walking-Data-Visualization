Select Judge.FirstName, Judge.LastName, 
max(case When Infraction='~' AND Color='Red' THEN MajorityNumber Else 0 END) DiscrepanciesLOCRed,
max(case When Infraction='<' AND Color='Red' THEN MajorityNumber Else 0 END) DiscrepanciesBentRed,
max(case When Infraction='~' AND Color='Yellow' THEN MajorityNumber Else 0 END) DiscrpanciesLOCYellow,
max(case When Infraction='<' AND Color='Yellow'THEN MajorityNumber Else 0 END) DiscrepanciesBentYellow
FROM
(SELECT JudgeCall.IDJudge, Count(JudgeCall.BibNumber) AS MajorityNumber , JudgeCall.Infraction, JudgeCall.Color
FROM JudgeCall LEFT JOIN
(SELECT JudgeCall.BibNumber, JudgeCall.IDRace, JudgeCall.Color, JudgeCall.Infraction
FROM JudgeCall 
WHERE JudgeCall.IDRace = 6
GROUP BY JudgeCall.BibNumber, JudgeCall.IDRace, JudgeCall.Color, JudgeCall.Infraction
HAVING (Count(JudgeCall.Infraction))>=(Select count(idJudge)/2 from RaceJudge WHERE RaceJudge.IDRace=6)) MajorityCallPerAthlete 
ON (JudgeCall.Infraction = MajorityCallPerAthlete.Infraction) AND (JudgeCall.Color = MajorityCallPerAthlete.Color) AND 
(JudgeCall.BibNumber = MajorityCallPerAthlete.BibNumber) AND (JudgeCall.IDRace = MajorityCallPerAthlete.IDRace)
WHERE (MajorityCallPerAthlete.BibNumber IS NULL) and JudgeCall.IDRace=6
GROUP BY JudgeCall.IDJudge, JudgeCall.Color, JudgeCall.Infraction) DiscrepanciesByJudge
LEFT JOIN Judge on Judge.IDJudge=DiscrepanciesByJudge.IDJudge
GROUP BY DiscrepanciesByJudge.IDJudge
ORDER BY DiscrepanciesByJudge.IDJudge, Judge.FirstName, Judge.LastName
