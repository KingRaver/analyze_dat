#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Union
import os
import logging
import time
import json
from logging.handlers import RotatingFileHandler
from datetime import datetime

class CorrelationLogger:
    def __init__(self) -> None:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Create analysis directory if it doesn't exist
        if not os.path.exists('logs/analysis'):
            os.makedirs('logs/analysis')

        # Setup main logger
        self.logger: logging.Logger = logging.getLogger('ETHBTCCorrelation')
        self.logger.setLevel(logging.INFO)

        # File handler with rotation (10MB max, keeping 5 backup files)
        file_handler = RotatingFileHandler(
            'logs/eth_btc_correlation.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )

        # Console handler
        console_handler = logging.StreamHandler()

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # API specific loggers
        self.coingecko_logger: logging.Logger = self._setup_api_logger('coingecko')
        self.claude_logger: logging.Logger = self._setup_api_logger('claude')
        
        # Analysis logger
        self.analysis_logger: logging.Logger = self._setup_analysis_logger()

    def _setup_api_logger(self, api_name: str) -> logging.Logger:
        """Setup specific logger for each API with its own file"""
        logger = logging.getLogger(f'ETHBTCCorrelation.{api_name}')
        logger.setLevel(logging.INFO)

        # Create API specific log file with rotation
        handler = RotatingFileHandler(
            f'logs/{api_name}_api.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _setup_analysis_logger(self) -> logging.Logger:
        """Setup specific logger for market analysis"""
        logger = logging.getLogger('ETHBTCCorrelation.analysis')
        logger.setLevel(logging.INFO)

        # Create analysis specific log file with rotation
        handler = RotatingFileHandler(
            'logs/analysis/market_analysis.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def log_coingecko_request(self, endpoint: str, success: bool = True) -> None:
        """Log Coingecko API interactions"""
        msg = f"CoinGecko API Request - Endpoint: {endpoint}"
        if success:
            self.coingecko_logger.info(msg)
        else:
            self.coingecko_logger.error(msg)

    def log_claude_analysis(
        self, 
        btc_price: float, 
        eth_price: float, 
        analysis: Optional[str] = None
    ) -> None:
        """Log Claude market sentiment analysis with enhanced details"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Log summary to main log
        msg = (
            f"Claude Market Analysis - "
            f"BTC Price: ${btc_price:,.2f} - "
            f"ETH Price: ${eth_price:,.2f}"
        )
        self.claude_logger.info(msg)
        
        # Save detailed analysis to separate file
        if analysis:
            analysis_file = f'logs/analysis/analysis_{timestamp}.json'
            try:
                analysis_data = {
                    'timestamp': timestamp,
                    'btc_price': btc_price,
                    'eth_price': eth_price,
                    'analysis': analysis,
                    'model': 'claude-3-5-sonnet-20241022'  # Added model tracking
                }
                with open(analysis_file, 'w') as f:
                    json.dump(analysis_data, f, indent=2)
                self.analysis_logger.info(f"Saved detailed analysis to {analysis_file}")
            except Exception as e:
                self.log_error("Analysis Logging", f"Failed to save analysis: {str(e)}")

    def log_market_correlation(
        self, 
        correlation_coefficient: float, 
        price_movement: float
    ) -> None:
        """Log market correlation details"""
        self.logger.info(
            "Market Correlation - "
            f"Correlation Coefficient: {correlation_coefficient:.2f} - "
            f"Price Movement: {price_movement:.2f}%"
        )

    def log_error(
        self, 
        error_type: str, 
        message: str, 
        exc_info: Union[bool, Exception, None] = None
    ) -> None:
        """Log errors with stack trace option"""
        self.logger.error(
            f"Error - Type: {error_type} - Message: {message}",
            exc_info=exc_info if exc_info else False
        )

    def log_twitter_action(self, action_type: str, status: str) -> None:
        """Log Twitter related actions"""
        self.logger.info(f"Twitter Action - Type: {action_type} - Status: {status}")

    def log_startup(self) -> None:
        """Log application startup"""
        self.logger.info("=" * 50)
        self.logger.info(f"ETH-BTC Correlation Bot Starting - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 50)

    def log_shutdown(self) -> None:
        """Log application shutdown"""
        self.logger.info("=" * 50)
        self.logger.info(f"ETH-BTC Correlation Bot Shutting Down - {time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 50)

# Singleton instance
logger = CorrelationLogger()
