import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
    // Recebe os dados do formData
    const formData = await req.formData();
    const file = formData.get("file");
    const chunkIndex = formData.get("chunkIndex");
    const totalChunks = formData.get("totalChunks");
    const fileName = formData.get("fileName");

    // Verifica se todos os dados necessários foram enviados
    if (!file || chunkIndex === null || totalChunks === null || !fileName) {
        return NextResponse.json(
            { status: 400, message: "Missing required fields" },
            { status: 400 }
        );
    }

    // Configura os dados para envio ao backend
    const backendFormData = new FormData();
    backendFormData.append("file", file);
    backendFormData.append("chunkIndex", chunkIndex.toString());
    backendFormData.append("totalChunks", totalChunks.toString());
    backendFormData.append("fileName", fileName.toString());

    const requestOptions = {
        method: "POST",
        body: backendFormData,
    };

    try {
        const response = await fetch(
            `${process.env.REST_API_BASE_URL}/api/upload-file/by-chunks/`,
            requestOptions
        );

        if (!response.ok) {
            return NextResponse.json(
                { status: response.status, message: response.statusText },
                { status: response.status }
            );
        }

        const result = await response.json();
        return NextResponse.json(result);
    } catch (error) {
        console.error("Erro ao processar CSV por chunks:", error);
        return NextResponse.json(
            { status: 500, message: "Internal server error" },
            { status: 500 }
        );
    }
}
