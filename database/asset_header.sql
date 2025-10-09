CREATE TABLE asset_header (
    symbol NVARCHAR(20) NOT NULL,                 
    asset_type NVARCHAR(20) NOT NULL,              
    exchange NVARCHAR(20) NOT NULL,                 
    asset_name NVARCHAR(255),                      
    industry NVARCHAR(100),                        
    sector NVARCHAR(100),                        
    currency CHAR(3),
    unit NVARCHAR(20),                                 
    market_cap DECIMAL(20,2),                     
    shares_outstanding BIGINT,                     
    updated_at DATETIME,        
    CONSTRAINT pk_asset PRIMARY KEY (symbol, exchange)
);
