import type { NextApiRequest, NextApiResponse } from "next";
import QuestionService from "@App/lib/question/QuestionService";


export default async function run_tests(
	req: NextApiRequest,
	res: NextApiResponse<{}>
) {
	const test_results = [];

	try {
		console.log("Testing getBySubject()...");
		const data = await QuestionService.getBySubject("math");
		test_results.push(
			{
				"Test": "getBySubject()",
				"Result": "Success",
				"Data": data.docs.map((doc) => doc.data())
			}
		);

		console.log("getBySubject() successful");
		console.log(data.docs.map((doc) => doc.data()));

	} catch (e) {
		
		console.log("Error in getBySubject():");
		console.log(e);

		test_results.push(
			{
				"Test": "getBySubject()",
				"Result": "Failure",
				"Error": e
			}
		);

	}

	try { 
		console.log("Testing getbyPosition()...");
		const data = await QuestionService.getByPosition("accountant");
		test_results.push(
			{
				"Test": "getByPosition()",
				"Result": "Success",
				"Data": data.docs.map((doc) => doc.data())
			}
		);

		console.log("getByPosition() successful");
		console.log(data.docs.map((doc) => doc.data()));

	} catch (e) { 
		console.log("Error in getByPosition():");
		console.log(e);

		test_results.push(
			{
				"Test": "getByPosition()",
				"Result": "Failure",
				"Error": e
			}
		);
	}

	try {
		console.log("Testing getByCompany()...");
		const data = await QuestionService.getByCompany(["amazon"]);
		test_results.push(
			{
				"Test": "getByCompany()",
				"Result": "Success",
				"Data": data.docs.map((doc) => doc.data())
			}
		);
	} catch (e) { 
		console.log("Error in getByCompany():");
		console.log(e);

		test_results.push(
			{
				"Test": "getByCompany()",
					"Result": "Failure",
				"Error": e
			}
		);
	}

	try {
		console.log("Testing getByType()...");
		const data = await QuestionService.getByType("behavioral");
		test_results.push(
			{
				"Test": "getByType()",
				"Result": "Success",
				"Data": data.docs.map((doc) => doc.data())
			}
		);
	} catch (e) {
		console.log("Error in getByType():");
		console.log(e);

		test_results.push(
			{
				"Test": "getByType()",
				"Result": "Failure",
				"Error": e
			}
		);
	}

	try {
		console.log("Testing getByPopularityDesc()...");
		const data = await QuestionService.getByPopularityDesc();
		test_results.push(
			{
				"Test": "getByPopularityDesc()",
				"Result": "Success",
				"Data": data.docs.map((doc) => doc.data())
			}
		);
	} catch (e) {
		console.log("Error in getByPopularityDesc():");
		console.log(e);

		test_results.push(
			{
				"Test": "getByPopularityDesc()",
				"Result": "Failure",
				"Error": e
			}
		);
	}

	try { 
		console.log("Testing updateQuestion()...")
		const data = await QuestionService.updateQuestion(
			{
				qid: "47MQn7GU7NHFRyXVtoLj",	// Harcoded for testing purposes
				popularity: 88
			}
		);

		console.log(data);
		test_results.push(
			{
				"Test": "updateQuestion()",
				"Result": "Success",
				"Data": data.data()
			}
		);


	} catch (e) { 
		console.log("Error in updateQuestion():");
		console.log(e);

		test_results.push(
			{
				"Test": "updateQuestion()",
				"Result": "Failure",
				"Error": e
			}
		);
	}

	try { 
		console.log("Testing deleteQuestion()...")
		const data = await QuestionService.deleteQuestion("1D3Rz2o2oZ4TbtJh4eLs");	// Harcoded for testing purposes

		console.log(data);
		test_results.push(
			{
				"Test": "deleteQuestion()",
				"Result": "Success",
				"Data": data.data()
			}
		);
	} catch (e) { 
		console.log("Error in deleteQuestion():");
		console.log(e);

		test_results.push(
			{
				"Test": "deleteQuestion()",
				"Result": "Failure",
				"Error": e
			}
		);
	}

	try { 
		console.log("Testing addCompanyToQuestion()...");
		const data = await QuestionService.addCompaniesToQuestion(
			
				"5EAsOCK2snOMElXT1PFH",	// Harcoded for testing purposes
				["comp1", "comp2"]
			
		);

		console.log(data);
		test_results.push(
			{
				"Test": "addCompanyToQuestion()",
				"Result": "Success",
				"Data": data.data()
			}
		);
	} catch (e) { 
		console.log("Error in addCompanyToQuestion():");
		console.log(e);

		test_results.push(
			{
				"Test": "addCompanyToQuestion()",
				"Result": "Failure",
				"Error": e
			}
		);
	}

	return res.status(200).json({ test_results: test_results })

}