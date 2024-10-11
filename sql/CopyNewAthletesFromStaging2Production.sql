INSERT INTO Athlete (IDAthlete, FirstName, LastName, CountryCode, Gender, BibNumber) 
SELECT AthleteStaging.IDAthlete, AthleteStaging.FirstName, AthleteStaging.LastName, AthleteStaging.CountryCode, AthleteStaging.Gender, AthleteStaging.BibNumber FROM AthleteStaging 
WHERE AthleteStaging.IDAthlete NOT IN (SELECT IDAthlete FROM Athlete) 