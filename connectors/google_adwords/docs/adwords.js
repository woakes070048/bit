Date.prototype.addDays = function(days) {
    this.setDate(this.getDate() + parseInt(days));
    return this;
};

function Storage(rootName, serviceAccount) {
    this.dateTime = new Date();
    this.configFileName = "config.json";
    this.account = AdWordsApp.currentAccount();
    this.timeZone = this.account.getTimeZone();
    this.rootName = rootName;
    this.rootFolder = this.createSubFolder(DriveApp.getRootFolder(), this.rootName);
    this.rootFolder.addEditor(serviceAccount);
    this.config = this.readConfig();
}

Storage.prototype.createSubFolder = function(folder, subFolderName){
    var it = folder.getFoldersByName(subFolderName);

    if(it.hasNext())
        return it.next();

    return folder.createFolder(subFolderName);
};

Storage.prototype.writeReport = function(tableName, date, rows){
    Logger.log("Saving report: " + tableName + " rows: " + rows.length);
    var dateName = Utilities.formatDate(date, this.timeZone, 'yyyy-MM-dd');
    var folder = this.createSubFolder(this.rootFolder, dateName);
    var fileName = tableName; //Utilities.formatString('%06d', partNumber);
    var blob = Utilities.newBlob(JSON.stringify(rows), MimeType.PLAIN_TEXT, fileName + ".json");
    var zip = Utilities.zip([blob]).setName(fileName + ".zip");
    this.writeBlob(folder, zip);
};

Storage.prototype.writeBlob = function (folder, blob) {
    var fileName = blob.getName();
    var files = folder.getFilesByName(fileName);

    while(files.hasNext()) {
        // Logger.log("Remove file:" + fileName);
        folder.removeFile(files.next());
    }

    // Logger.log("Create file: " + fileName);
    folder.createFile(blob);
};

Storage.prototype.saveConfig = function () {
    var files = this.rootFolder.getFilesByName(this.configFileName);
    var configFile = null;
    if (files.hasNext())
        configFile = files.next();

    var content = JSON.stringify(this.config);

    if(configFile == null ) {
        Logger.log("Create config file: " + content);
        this.rootFolder.createFile(this.configFileName, content);
    }
    else {
        Logger.log("Save config file:" + content);
        configFile.setContent(content);
    }
};

Storage.prototype.defaultConfig = function () {
    var firstDate = null;
    var it = AdWordsApp.campaigns().get();
    while(it.hasNext()){
        var campaign = it.next();
        var startDate = campaign.getStartDate();
        var campaignDate = new Date(startDate.year, startDate.month, startDate.day);
        if(firstDate==null || campaignDate < firstDate)
              firstDate = campaignDate;
    }
    return  {
        lastDate: Utilities.formatDate(firstDate, this.timeZone, 'yyyy/MM/dd')
    }
};

Storage.prototype.readConfig = function () {
    var files = this.rootFolder.getFilesByName(this.configFileName);
    var configFile = null;
    if (files.hasNext()) {
        configFile = files.next();
    }
    if(configFile != null ){
        Logger.log("Read config file:" + configFile.getName());
        var content = configFile.getBlob().getDataAsString();
        return JSON.parse(content);
    }
    return this.defaultConfig();

};

function Etl(rootFolder, googleDriveServiceAccount){
    this.drive = new Storage(rootFolder, googleDriveServiceAccount);
}

Etl.prototype.setLastReportDate = function(date){
    this.drive.config.lastDate = Utilities.formatDate(date, this.drive.timeZone, 'yyyy/MM/dd');
    this.drive.saveConfig();
};

Etl.prototype.getLastReportDate = function(){
    Logger.log("Last date:" + this.drive.config.lastDate);
    return new Date(this.drive.config.lastDate);
};

Etl.prototype.REPORT_BASE_FIELDS = [
    'Date',
    'CampaignId',
    'CampaignName',
    'Clicks',
    'Conversions',
    'Cost',
    'Device',
    'Impressions'
];

Etl.prototype.PERFORMANCE_REPORTS = [
    {
        table: 'CAMPAIGN_PERFORMANCE_REPORT',
        fields: []
    },
    {
        table: 'GENDER_PERFORMANCE_REPORT',
        fields: [
            'Id',
            'Criteria'
        ]
    },
    {
        table: 'PLACEHOLDER_FEED_ITEM_REPORT',
        fields: [
            'Criteria',
            'FeedId',
            'FeedItemId',
            'GeoTargetingCriterionId',
            'GeoTargetingRestriction',
        ]
    },
    {
        table: 'GEO_PERFORMANCE_REPORT',
        fields: [
            'CountryCriteriaId',
            'CityCriteriaId',
            'IsTargetingLocation',
            'LocationType',
            'MetroCriteriaId'
        ]
    },
    /* {
        table: 'KEYWORDS_PERFORMANCE_REPORT',
        fields: [
            'Criteria',
            'QualityScore',
            'Slot'
        ]
    },*/
    {
        table: 'SEARCH_QUERY_PERFORMANCE_REPORT',
        fields: [
            'KeywordId',
            'KeywordTextMatchingQuery',
            'QueryMatchTypeWithVariant',

        ]
    },
    /*{
        table: 'PAID_ORGANIC_QUERY_REPORT',
        fields: [

            'OrganicClicks',
            'OrganicClicksPerQuery',
            'OrganicImpressions',
            'OrganicImpressionsPerQuery',
            'OrganicQueries',
            'SearchQuery',
            'QueryMatchType'
        ]
    },*/
    {
        table: 'PLACEMENT_PERFORMANCE_REPORT',
        fields: [
            'Id',
            'Criteria'
        ]
    }

];

Etl.prototype.exportReport = function(reportInfo, since){

    Logger.log("Processing report: " + reportInfo.table);
    var fieldNames = this.REPORT_BASE_FIELDS.concat(reportInfo.fields).join(", ");
    // Logger.log('Fields: ' + fieldNames);

    var since_str = Utilities.formatDate(since, this.drive.timeZone, 'yyyyMMdd');
    //var until_str = Utilities.formatDate(since, this.drive.timeZone, 'yyyyMMdd');

    var sql = 'SELECT ' + fieldNames +
        ' FROM ' + reportInfo.table +
        ' DURING ' + since_str + "," + since_str;

    //Logger.log("sql: " + sql);

    var report = AdWordsApp.report(sql);
    /*
    var spreadsheetName = "z-analytics - " + since_str + "_" + until_str + " - " + reportInfo.table;
    Logger.log("Export to spreadsheet: " + spreadsheetName);
    var spreadsheet = SpreadsheetApp.create(spreadsheetName);

    report.exportToSheet(spreadsheet.getActiveSheet());

    return; */

    var queryIterator = report.rows();

    var rows = [];
    var partNumber = 0;
    // var partSize = 30000;
    var totalRows = 0;

    // Iterate over each row.
    while (queryIterator.hasNext()) {
        var row = queryIterator.next();
        rows.push(row);
        // if(rows.length == partSize){
        //     this.drive.writeReport(reportInfo.table, date, partNumber, rows);
        //     totalRows += rows.length;
        //     rows = [];
        //     partNumber = partNumber + 1;
        // }

    }

    totalRows += rows.length;

    this.drive.writeReport(reportInfo.table, since, rows);


    Logger.log("Total rows: " + totalRows);
};

Etl.prototype.run = function () {
    var since = this.getLastReportDate();
    var yesterday = new Date();
    yesterday.addDays(-1);

    while(since <= yesterday) {
        // var until = new Date(since);
        // until.addDays(1);

        // if(until > yesterday)
        //     until = yesterday;
        //
        // Logger.log("Run reports since: " + since + " until: " + until);

        for (var i = 0; i < this.PERFORMANCE_REPORTS.length; i++) {
            this.exportReport(this.PERFORMANCE_REPORTS[i], since);
        }
        // since = until;
        since.addDays(1);
        this.setLastReportDate(since);
        //break;

    }

};

function main() {
    var etl = new Etl('bit', 'drive-993@project-id-8281928869006252347.iam.gserviceaccount.com');
    etl.run();
}
