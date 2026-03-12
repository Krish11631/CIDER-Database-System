-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: localhost    Database: cider_crime
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `case_file`
--

DROP TABLE IF EXISTS `case_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `case_file` (
  `Case_ID` int NOT NULL,
  `Crime_Type` varchar(50) NOT NULL,
  `Description` text,
  `Paper_Number` varchar(50) NOT NULL,
  `Incident_Date` date NOT NULL,
  `Incident_Time` time NOT NULL,
  `Location` varchar(150) DEFAULT NULL,
  `Status` varchar(20) DEFAULT 'Active',
  `Branch_ID` int NOT NULL,
  PRIMARY KEY (`Case_ID`),
  UNIQUE KEY `Paper_Number` (`Paper_Number`),
  KEY `Branch_ID` (`Branch_ID`),
  KEY `idx_crime_type` (`Crime_Type`),
  CONSTRAINT `case_file_ibfk_1` FOREIGN KEY (`Branch_ID`) REFERENCES `cider_hr`.`branch` (`Branch_ID`),
  CONSTRAINT `case_file_chk_1` CHECK ((`Crime_Type` in (_utf8mb4'Terrorism',_utf8mb4'Normal'))),
  CONSTRAINT `case_file_chk_2` CHECK ((`Status` in (_utf8mb4'Active',_utf8mb4'Pending',_utf8mb4'Solved')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `case_file`
--

LOCK TABLES `case_file` WRITE;
/*!40000 ALTER TABLE `case_file` DISABLE KEYS */;
INSERT INTO `case_file` VALUES (1002,'Normal','Credit card skimming racket','FILE-2026-002','2026-01-15','09:00:00','Nehru Place','Active',1),(1003,'Normal','Armed robbery at jewelry store','FILE-2026-003','2025-12-25','20:15:00','Karol Bagh','Active',2);
/*!40000 ALTER TABLE `case_file` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-12 13:46:20
