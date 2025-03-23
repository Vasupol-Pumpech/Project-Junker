-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 05, 2025 at 04:22 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";
/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
--
-- Database: `junker`
--
-- --------------------------------------------------------
--
-- Table structure for table `tbl_bin`
--
CREATE TABLE `tbl_bin` (
  `bin_id` int(11) NOT NULL,
  `bin_location` varchar(40) DEFAULT NULL,
  `bin_status` tinyint(1) DEFAULT NULL,
  `bin_level` int(11) DEFAULT NULL,
  `bin_notify` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Dumping data for table `tbl_bin`
--
-- --------------------------------------------------------
--
-- Table structure for table `tbl_bin_detail`
--
CREATE TABLE `tbl_bin_detail` (
  `bin_id` int(11) NOT NULL,
  `bottle_amount` int(11) DEFAULT NULL,
  `can_amount` int(11) DEFAULT NULL,
  `papercup_amount` int(11) DEFAULT NULL,
  `others_amount` int(11) DEFAULT NULL,
  `amount_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Dumping data for table `tbl_bin_detail`
--
-- --------------------------------------------------------
--
-- Table structure for table `tbl_garbage`
--
CREATE TABLE `tbl_garbage` (
  `garbage_id` int(11) NOT NULL,
  `bin_id` int(11) DEFAULT NULL,
  `garbage_type` tinytext DEFAULT NULL,
  `garbage_date` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `garbage_img` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Dumping data for table `tbl_garbage`
--
-- --------------------------------------------------------
--
-- Table structure for table `tbl_report`
--
CREATE TABLE `tbl_report` (
  `report_id` int(11) NOT NULL,
  `bin_id` int(11) DEFAULT NULL,
  `report_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `report_status` tinyint(1) DEFAULT NULL,
  `report_message` varchar(100) DEFAULT NULL,
  `report_edit_date` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Dumping data for table `tbl_report`
--
-- --------------------------------------------------------
--
-- Table structure for table `tbl_users`
--
CREATE TABLE `tbl_users` (
  `chat_id` bigint(20) NOT NULL,
  `name` varchar(255) NOT NULL,
  `role` enum('user','admin') DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Dumping data for table `tbl_users`
--
--
-- Indexes for dumped tables
--
--
-- Indexes for table `tbl_bin`
--
ALTER TABLE `tbl_bin`
  ADD PRIMARY KEY (`bin_id`);
--
-- Indexes for table `tbl_bin_detail`
--
ALTER TABLE `tbl_bin_detail`
  ADD PRIMARY KEY (`bin_id`);
--
-- Indexes for table `tbl_garbage`
--
ALTER TABLE `tbl_garbage`
  ADD PRIMARY KEY (`garbage_id`),
  ADD KEY `bin_id` (`bin_id`);
--
-- Indexes for table `tbl_report`
--
ALTER TABLE `tbl_report`
  ADD PRIMARY KEY (`report_id`),
  ADD KEY `bin_id` (`bin_id`);
--
-- Indexes for table `tbl_users`
--
ALTER TABLE `tbl_users`
  ADD PRIMARY KEY (`chat_id`);
--
-- AUTO_INCREMENT for dumped tables
--
--
-- AUTO_INCREMENT for table `tbl_bin`
--
ALTER TABLE `tbl_bin`
  MODIFY `bin_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT for table `tbl_garbage`
--
ALTER TABLE `tbl_garbage`
  MODIFY `garbage_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=427;
--
-- AUTO_INCREMENT for table `tbl_report`
--
ALTER TABLE `tbl_report`
  MODIFY `report_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=185;
--
-- Constraints for dumped tables
--
--
-- Constraints for table `tbl_bin_detail`
--
ALTER TABLE `tbl_bin_detail`
  ADD CONSTRAINT `tbl_bin_detail_ibfk_1` FOREIGN KEY (`bin_id`) REFERENCES `tbl_bin` (`bin_id`);
--
-- Constraints for table `tbl_garbage`
--
ALTER TABLE `tbl_garbage`
  ADD CONSTRAINT `tbl_garbage_ibfk_1` FOREIGN KEY (`bin_id`) REFERENCES `tbl_bin` (`bin_id`);
--
-- Constraints for table `tbl_report`
--
ALTER TABLE `tbl_report`
  ADD CONSTRAINT `tbl_report_ibfk_1` FOREIGN KEY (`bin_id`) REFERENCES `tbl_bin` (`bin_id`);
COMMIT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;


INSERT INTO `tbl_bin` (`bin_id`, `bin_location`, `bin_status`, `bin_level`, `bin_notify`) VALUES 
(1, 'ภาคคอม ชั้น 1', 0, 90, 70);

INSERT INTO `tbl_bin_detail` (`bin_id`, `bottle_amount`, `can_amount`, `papercup_amount`, `others_amount`, `amount_time`) VALUES
(1, 0, 0, 0, 0, '2025-03-05 14:11:43');
